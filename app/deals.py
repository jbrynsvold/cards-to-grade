from app.discord_alerts import send_discord_alert

# Simple dedupe cache to avoid duplicate alerts
dedupe_cache = set()

BLOCKED_KEYWORDS = ["japanese", "japan"]

def calculate_psa_profit(price):
    """Estimate profit for a PSA graded card"""
    return round(price * 0.85 - 25, 2)

def calculate_profit_margin(profit, cost):
    """Return profit margin percentage"""
    if cost == 0:
        return 0.0
    return round((profit / cost) * 100, 2)

def is_blocked_title(title: str) -> bool:
    t = title.lower()
    return any(word in t for word in BLOCKED_KEYWORDS)

async def process_ebay_results_batch(session, ebay_client, semaphore, card):
    """
    Search eBay listings for a card and send Discord alerts for Buy It Now listings
    that are under market_avg price and meet PSA profit thresholds.
    """
    async with semaphore:
        listings = await ebay_client.search_listings(session, card)

        if not listings:
            print(f"[Deals] No Buy It Now listings under market_avg for '{card['card_name']}'")
            return

        for listing in listings:
            try:
                title = listing.get("title", "")

                # 🚫 Filter Japanese listings
                if is_blocked_title(title):
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

                # Calculate PSA profit/margin
                psa_profit = calculate_psa_profit(card.get("psa_10_price", 0))
                psa_margin = calculate_profit_margin(psa_profit, price)

                if psa_margin < 100:
                    continue

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
                    "psa_10_profit": psa_profit,
                    "psa_10_margin": psa_margin,
                    "psa_9_price": card.get("psa_9_price"),
                    "psa_9_profit": calculate_psa_profit(card.get("psa_9_price", 0)),
                    "velocity": card.get("velocity"),
                    "url": listing.get("itemWebUrl") or "URL not available"
                }

                await send_discord_alert(alert_data)

            except Exception as e:
                print(f"[Deals] Error processing listing '{listing.get('title', 'UNKNOWN')}': {e}")
