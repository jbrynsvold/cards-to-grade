from app.discord import send_discord_alert


def calculate_profit(price):
    return (price * 0.85) - 25


async def process_ebay_results_batch(card, listings, seen_listings):
    for listing in listings:
        # Deduplicate by URL or itemId
        listing_id = listing.get("url") or listing.get("itemId")
        if not listing_id or listing_id in seen_listings:
            continue
        seen_listings.add(listing_id)

        try:
            price = float(listing["price"]["value"])
        except:
            continue

        psa10_profit = calculate_profit(card["psa10_price"])
        psa9_profit = calculate_profit(card["psa9_price"])

        psa10_margin = (psa10_profit / price * 100) if price else 0
        psa9_margin = (psa9_profit / price * 100) if price else 0

        # Only alert if PSA 10 profit margin >= 100%
        if psa10_margin < 100:
            continue

        alert_data = {
            "card": card,
            "listing": listing,
            "price": price,
            "psa10_profit": psa10_profit,
            "psa9_profit": psa9_profit,
            "psa10_margin": psa10_margin,
            "psa9_margin": psa9_margin,
        }

        await send_discord_alert(alert_data)
