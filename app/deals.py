from app.ebay import extract_price, extract_listing_url
from app.discord import send_discord_alert
from app.config import DEAL_THRESHOLD


async def process_ebay_results_batch(card, listings):
    if not listings:
        return

    market_price = card["avg"]

    for listing in listings:
        try:
            price = extract_price(listing)
            if price <= 0:
                continue

            if price <= market_price * DEAL_THRESHOLD:
                listing["parsed_price"] = price
                listing["resolved_url"] = extract_listing_url(listing)

                print(f"[Deal] {card['player']} - ${price:.2f}")

                await send_discord_alert(card, listing)

        except Exception as e:
            print("[Deals] Error:", e)
