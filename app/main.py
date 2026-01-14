import asyncio
import aiohttp
from app.sheets import load_cards
from app.ebay import EbayClient
from app.deals import process_ebay_results_batch
from app.config import EBAY_CONCURRENT_REQUESTS, BATCH_DELAY_SECONDS

async def worker(card, session, ebay_client, semaphore):
    await process_ebay_results_batch(session, ebay_client, semaphore, card)

async def run_bot():
    cards = load_cards()
    semaphore = asyncio.Semaphore(EBAY_CONCURRENT_REQUESTS)
    ebay_client = EbayClient()

    async with aiohttp.ClientSession() as session:
        while True:
            print("[Main] Starting scan cycle...")
            tasks = [worker(card, session, ebay_client, semaphore) for card in cards]
            await asyncio.gather(*tasks)
            print(f"[Main] Cycle complete. Sleeping {BATCH_DELAY_SECONDS}s\n")
            await asyncio.sleep(BATCH_DELAY_SECONDS)

if __name__ == "__main__":
    asyncio.run(run_bot())
