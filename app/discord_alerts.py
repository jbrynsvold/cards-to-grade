import aiohttp
from config import DISCORD_WEBHOOK_URL

async def send_discord_alert(message: str):
    if not DISCORD_WEBHOOK_URL:
        print("[Discord] No webhook URL configured.")
        return

    async with aiohttp.ClientSession() as session:
        payload = {"content": message}
        async with session.post(DISCORD_WEBHOOK_URL, json=payload) as resp:
            if resp.status != 204:
                print(f"[Discord] Failed to send alert: {resp.status}")
