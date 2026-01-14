import aiohttp
from app.config import DISCORD_WEBHOOK_URL


async def send_discord_alert(data):
    card = data["card"]
    listing = data["listing"]

    content = f"""
**Card:** {card['card_name']} {card['set']} #{card['number']} {card['parallel']}
**eBay Listing:** {listing['title']}
**eBay Price:** ${data['price']:.2f}
**Market Average Price:** ${card['market_avg']:.2f}
**PSA 10 Price:** ${card['psa10_price']:.2f}
**PSA 10 Profit:** ${data['psa10_profit']:.2f}
**PSA 10 Profit Margin:** {data['psa10_margin']:.2f}%
**PSA 9 Price:** ${card['psa9_price']:.2f}
**PSA 9 Profit:** ${data['psa9_profit']:.2f}
**PSA 9 Profit Margin:** {data['psa9_margin']:.2f}%
**Velocity:** {card['velocity']}
**Link:** {listing['url']}
"""

    payload = {"content": content}

    async with aiohttp.ClientSession() as session:
        await session.post(DISCORD_WEBHOOK_URL, json=payload)
