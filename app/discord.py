import aiohttp
from app.config import DISCORD_WEBHOOK_URL


async def send_discord_alert(card, listing):

    if not DISCORD_WEBHOOK_URL:
        return

    price = listing["parsed_price"]
    url = listing["resolved_url"]

    message = f"""
🔥 **Sports Card Deal Found**

**Card:** {card['card']}
**Player:** {card['player']}
**Sport:** {card['sport']}
**Set:** {card['set']}
**Number:** {card['number']}
**Parallel:** {card['parallel']}
**Grade:** {card['grade']}

📊 **Market Avg:** ${card['avg']:.2f}
💵 **Listing Price:** ${price:.2f}

🏆 **PSA 10 Price:** ${card['psa10_price']:.2f}
🏅 **PSA 9 Price:** ${card['psa9_price']:.2f}

💰 **PSA 10 Profit:** ${card['psa10_profit']:.2f}
💰 **PSA 9 Profit:** ${card['psa9_profit']:.2f}

⚡ **Velocity (30d):** {card['velocity']} sales

🔗 {url}
"""

    async with aiohttp.ClientSession() as session:
        async with session.post(DISCORD_WEBHOOK_URL, json={"content": message}) as resp:
            if resp.status != 204:
                text = await resp.text()
                print("[Discord]", resp.status, text)
