import asyncio
from app.discord import send_discord_alert

SENT_ALERTS = set()

def calculate_profit(price):
    """Profit = (PSA 10 Price * 0.85) - 25"""
    return round(price * 0.85 - 25, 2)

async def process_ebay_results_batch(card, listings):
    for listing in listings:
        key = (card["card_name"], listing["url"])
        if key in SENT_ALERTS:
            continue  # dedupe
        SENT_ALERTS.add(key)

        psa_10_profit = calculate_profit(card["psa_10_price"])
        psa_10_margin = (psa_10_profit / card["psa_10_price"] * 100) if card["psa_10_price"] else 0

        if psa_10_margin < 100:
            continue  # skip if profit margin < 100%

        psa_9_profit = calculate_profit(card["psa_9_price"])
        psa_9_margin = (psa_9_profit / card["psa_9_price"] * 100) if card["psa_9_price"] else 0

        alert_payload = {
            "card_name": card["card_name"],
            "listing_title": listing["title"],
            "listing_url": listing["url"],
            "listing_price": listing["price"],
            "market_avg": card["market_avg"],
            "psa_10_price": card["psa_10_price"],
            "psa_10_profit": psa_10_profit,
            "psa_10_margin": psa_10_margin,
            "psa_9_price": card["psa_9_price"],
            "psa_9_profit": psa_9_profit,
            "psa_9_margin": psa_9_margin,
            "velocity": card["velocity"],
        }

        await send_discord_alert(alert_payload, listing)
        await asyncio.sleep(0.5)  # slight throttle
