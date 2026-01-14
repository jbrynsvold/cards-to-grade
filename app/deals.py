from app.discord_alerts import send_discord_alert

dedupe_cache = set()

def calculate_psa_profit(price):
    return round(price * 0.85 - 25, 2)

def calculate_profit_margin(profit, cost):
    if cost == 0:
        return 0.0
    return round((profit / cost) * 100, 2)

async def process_ebay_results_batch(session, ebay_client, semaphore, card):
    async with semaphore:
        listings = await ebay_client.search_listings(session, card)

        # Log the search string instead of card_name with number
        player = card.get("player", "")
        set_name = card.get("set", "")
        parallel = card.get("parallel", "")
        query_str = f"{player} {set_name} {parallel}".strip()

        if not listings:
            print(f"[Deals] No listings found for {query_str}")
            return

        for listing in listings:
            try:
                item_id = listing.get("itemId") or listing.get("url")
                if item_id in dedupe_cache:
                    continue
                dedupe_cache.add(item_id)

                price = float(str(listing.get("price", 0)).replace("$", "").replace(",", "").strip())
                psa_profit = calculate_psa_profit(card["psa_10_price"])
                psa_margin = calculate_profit_margin(psa_profit, price)

                if psa_margin < 100:
                    continue

                alert_data = {
                    "card_name": card["card_name"],
                    "player": player,
                    "set": set_name,
                    "card_number": card.get("card_number", ""),
                    "parallel": parallel,
                    "sport": card.get("sport", ""),
                    "ebay_title": listing.get("title", "No title"),
                    "ebay_price": price,
                    "market_avg": card["market_avg"],
                    "psa_10_price": card["psa_10_price"],
                    "psa_10_profit": psa_profit,
                    "psa_10_margin": psa_margin,
                    "psa_9_price": card["psa_9_price"],
                    "psa_9_profit": calculate_psa_profit(card["psa_9_price"]),
                    "velocity": card["velocity"],
                    "url": listing.get("url") or "URL not available"
                }

                await send_discord_alert(alert_data)
            except Exception as e:
                print(f"[Deals] Error processing listing for {query_str}: {e}")
