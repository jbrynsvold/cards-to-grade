import asyncio
from app.ebay import search_ebay_listings
from app.discord import send_discord_alert

async def process_ebay_results_batch(card, listings):
    """
    Process eBay search results for a single card.
    Sends alerts to Discord if found.
    """
    if not listings:
        print(f"[Deals] No listings found for {card['card_name']}")
        return

    for listing in listings:
        try:
            price_field = listing.get("price")
            if isinstance(price_field, dict):
                price_field = price_field.get("value")
            price = float(str(price_field).replace("$", "").replace(",", "").strip())
            if price <= 0:
                continue

            url = listing.get("url") or listing.get("itemUrl") or "URL not available"
            await send_discord_alert(card, listing, url=url, listing_price=price)

        except Exception as e:
            print(f"[Deals] Skipping listing due to error: {e}")
            continue
