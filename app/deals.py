import asyncio
from app.ebay import fetch_ebay_listings
from app.discord_alerts import send_discord_alert

async def process_ebay_results_batch(semaphore, card, listings):
    async with semaphore:
        results = await fetch_ebay_listings(card["name"])
        for item in results:
            if item["price"] < card.get("tcg_price", 0):
                await send_discord_alert(f"Deal found: {item['title']} at ${item['price']}\n{item['link']}")
