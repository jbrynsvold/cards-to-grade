from app.discord import send_discord_alert

def calculate_psa_profit(price):
    """PSA Profit = (PSA Price * 0.85) - 25"""
    return round(price * 0.85 - 25, 2)

def calculate_profit_margin(profit, cost):
    if cost == 0:
        return 0.0
    return round((profit / cost) * 100, 2)

dedupe_cache = set()

async def process_ebay_results_batch(session, ebay_client, semaphore, card):
    """
    Search eBay for a card and send alerts for listings that meet PSA 10 profit margin ≥100%.
    """
    async with semaphore:
        listings = await ebay_client.search_listings(session, card)
        if not listings:
            print(f"[Deals] No listings found for {card['card_name']}")
            return

        for listing in listings:
            try:
                # Deduplicate by eBay item ID
                item_id = listing.get("itemId") or listing.get("id") or listing.get("url")
                if item_id in dedupe_cache:
                    continue
                dedupe_cache.add(item_id)

                price_str = listing.get("price")
                if isinstance(price_str, dict):
                    price = float(price_str.get("value", 0))
                else:
                    price = float(str(price_str).replace("$", "").replace(",", "").strip())

                psa_10_profit = calculate_psa_profit(card["psa_10_price"])
                psa_10_margin = calculate_profit_margin(psa_10_profit, price)

                if psa_10_margin < 100:  # Filter
                    continue

                alert_data = {
                    "card_name": card["card_name"],
                    "player": card["player"],
                    "set": card["set"],
                    "card_number": card["card_number"],
                    "parallel": card["parallel"],
                    "sport": card["sport"],
                    "ebay_title": listing.get("title", "No title"),
                    "ebay_price": price,
                    "market_avg": card["market_avg"],
                    "psa_10_price": card["psa_10_price"],
                    "psa_10_profit": psa_10_profit,
                    "psa_10_margin": psa_10_margin,
                    "psa_9_price": card["psa_9_price"],
                    "psa_9_profit": calculate_psa_profit(card["psa_9_price"]),
                    "velocity": card["velocity"],
                    "url": listing.get("url") or "URL not available"
                }

                await send_discord_alert(alert_data)

            except Exception as e:
                print(f"[Deals] Error processing listing: {e}")
                continue
