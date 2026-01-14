import asyncio
import aiohttp
from app.sheets import load_cards
from app.ebay import EbayClient
from app.deals import process_ebay_results_batch
from app.config import EBAY_CONCURRENT_REQUESTS, BATCH_DELAY_SECONDS

CARDS_REFRESH_INTERVAL = 3 * 60 * 60  # 3 hours

cards = []

async def refresh_cards_periodically():
    """Reload the Google Sheet every few hours"""
    global cards
    while True:
        try:
            new_cards = load_cards()
            cards = new_cards
            print(f"[Sheets] Reloaded {len(cards)} cards from sheet.")
        except Exception as e:
            print(f"[Sheets] Error reloading cards: {e}")
        await asyncio.sleep(CARDS_REFRESH_INTERVAL)

async def worker(card, session, ebay_client, semaphore):
    await process_ebay_results_batch(session, ebay_client, semaphore, card)

async def run_bot():
    global cards
    # Initial load
    cards = load_cards()
    semaphore = asyncio.Semaphore(EBAY_CONCURRENT_REQUESTS)
    ebay_client = EbayClient()

    async with aiohttp.ClientSession() as session:
        # Start background sheet refresh
        asyncio.create_task(refresh_cards_periodically())

        while True:
            if not cards:
                print("[Main] No cards loaded yet, waiting 60s...")
                await asyncio.sleep(60)
                continue

            print("[Main] Starting scan cycle...")
            tasks = [worker(card, session, ebay_client, semaphore) for card in cards]
            await asyncio.gather(*tasks)
            print(f"[Main] Cycle complete. Sleeping {BATCH_DELAY_SECONDS}s\n")
            await asyncio.sleep(BATCH_DELAY_SECONDS)

if __name__ == "__main__":
    asyncio.run(run_bot())
