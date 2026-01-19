import aiohttp
from app.config import DISCORD_WEBHOOK_URL

async def send_discord_alert(alert_data):
    if not DISCORD_WEBHOOK_URL:
        print("[Discord] No webhook URL configured.")
        return

    msg = (
        f"Card: {alert_data['card_name']} {alert_data['set']} {alert_data['parallel']}\n"
        f"eBay Listing: {alert_data['ebay_title']}\n"
        f"eBay Price: ${alert_data['ebay_price']:.2f}\n"
        f"Market Avg Price: ${alert_data['market_avg']:.2f}\n"
        f"PSA 10 Price: ${alert_data['psa_10_price']:.2f}\n"
        f"PSA 10 Profit: ${alert_data['psa_10_profit']:.2f}\n"
        f"PSA 10 Profit Margin: {alert_data['psa_10_margin']:.2f}%\n"
        f"PSA 9 Price: ${alert_data['psa_9_price']:.2f}\n"
        f"PSA 9 Profit: ${alert_data['psa_9_profit']:.2f}\n"
        f"PSA 9 Profit Margin: {alert_data['psa_9_margin']:.2f}%\n"
        f"Velocity: {alert_data['velocity']}\n"
        f"Link: {alert_data['url']}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.post(DISCORD_WEBHOOK_URL, json={"content": msg}) as resp:
            if resp.status != 204:
                print(f"[Discord] Failed to send alert: {resp.status}")
