import asyncio
from app.sheets import load_cards
from app.deals import process_ebay_results_batch
from app.config import CONCURRENT_EBAY_REQUESTS

async def worker(card, semaphore):
    await process_ebay_results_batch(semaphore, card, [])

async def run_bot():
    cards = load_cards()
    semaphore = asyncio.Semaphore(CONCURRENT_EBAY_REQUESTS)

    tasks = [worker(card, semaphore) for card in cards]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    print("[Main] Starting scan cycle...")
    asyncio.run(run_bot())
