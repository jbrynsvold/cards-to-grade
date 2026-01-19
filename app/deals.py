from app.discord_alerts import send_discord_alert
import re

# Simple dedupe cache to avoid duplicate alerts
dedupe_cache = set()

BLOCKED_KEYWORDS = ["japanese", "japan"]
CARD_NUMBER_REGEX = re.compile(r"#\s*([A-Za-z0-9/]+)")

def is_blocked_title(title: str) -> bool:
    t = title.lower()
    return any(word in t for word in BLOCKED_KEYWORDS)

def extract_card_number_from_title(title: str):
    match = CARD_NUMBER_REGEX.search(title)
    if not match:
        return None
    return match.group(1).lower().replace(" ", "")

def normalize_card_number(num):
    if not num:
        return None
    return str(num).lower().replace(" ", "")

async def process_ebay_results_batch(session, ebay_client, semaphore, card):
    async with semaphore:
        listings = await ebay_client.search_listings(session, card)

        if not listings:
            print(f"[Deals] No Buy It Now listings under market_avg for '{card['card_name']}'")
            return

        sheet_card_number = normalize_card_number(
            card.get("number") or card.get("card_number")
        )

        for listing in listings:
            try:
                title = listing.get("title", "")

                # 🚫 Filter Japanese listings
                if is_blocked_title(title):
                    continue

                # 🔢 Card number validation (only if title contains one)
                title_card_number = extract_card_number_from_title(title)
                if title_card_number and sheet_card_number:
                    if title_card_number != sheet_card_number:
                        continue

                # Unique ID for dedupe
                item_id = listing.get("itemId") or listing.get("itemWebUrl")
                if item_id in dedupe_cache:
                    continue
                dedupe_cache.add(item_id)

                # Extract price safely
                price_str = listing.get("price", {}).get("value") or listing.get("price", 0)
                try:
                    price = float(price_str)
                except:
                    price = 0.0

                # Skip listings above market_avg
                if price > card.get("market_avg", 0):
                    continue

                # Pull PSA profit/margin directly from sheet columns
                psa_10_profit = card.get("PSA 10 Profit") or card.get("psa_10_profit") or 0
                psa_10_margin = card.get("PSA 10 Profit Margin") or card.get("psa_10_margin") or 0
                psa_9_profit = card.get("PSA 9 Profit") or card.get("psa_9_profit") or 0
                psa_9_margin = card.get("PSA 9 Profit Margin") or card.get("psa_9_margin") or 0

                alert_data = {
                    "card_name": card.get("card_name"),
                    "player": card.get("player"),
                    "set": card.get("set"),
                    "parallel": card.get("parallel"),
                    "sport": card.get("sport"),
                    "ebay_title": title,
                    "ebay_price": price,
                    "market_avg": card.get("market_avg"),
                    "psa_10_price": card.get("psa_10_price"),
                    "psa_10_profit": psa_10_profit,
                    "psa_10_margin": psa_10_margin,
                    "psa_9_price": card.get("psa_9_price"),
                    "psa_9_profit": psa_9_profit,
                    "psa_9_margin": psa_9_margin,
                    "velocity": card.get("velocity"),
                    "url": listing.get("itemWebUrl") or "URL not available"
                }

                await send_discord_alert(alert_data)

            except Exception as e:
                print(f"[Deals] Error processing listing '{listing.get('title', 'UNKNOWN')}': {e}")
