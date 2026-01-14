import asyncio
import aiohttp

from app.config import EBAY_CONCURRENT_REQUESTS, BATCH_DELAY_SECONDS
from app.sheets import load_cards
from app.ebay import search_ebay_listings
from app.deals import process_ebay_results_batch

async def worker(semaphore, session, card):
    async with semaphore:
        listings = await search_ebay_listings(session, card)
        await process_ebay_results_batch(card, listings)

async def run_bot():
    cards = load_cards()
    semaphore = asyncio.Semaphore(EBAY_CONCURRENT_REQUESTS)

    async with aiohttp.ClientSession() as session:
        while True:
            print("[Main] Starting scan cycle...")
            tasks = [worker(semaphore, session, card) for card in cards]
            await asyncio.gather(*tasks)
            print(f"[Main] Cycle complete. Sleeping {BATCH_DELAY_SECONDS}s\n")
            await asyncio.sleep(BATCH_DELAY_SECONDS)

if __name__ == "__main__":
    asyncio.run(run_bot())
