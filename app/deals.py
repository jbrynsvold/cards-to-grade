import asyncio
from ebay import fetch_ebay_listings
from discord_alerts import send_discord_alert

async def process_ebay_results_batch(semaphore, card, listings):
    async with semaphore:
        results = await fetch_ebay_listings(card["name"])
        for item in results:
            # Simple filter example: alert if below TCG Price
            if item["price"] < card.get("tcg_price", 0):
                await send_discord_alert(f"Deal found: {item['title']} at ${item['price']}\n{item['link']}")
