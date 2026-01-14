import os
import aiohttp

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not DISCORD_WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK_URL not set in environment variables.")

async def send_discord_alert(card, listing):
    """
    Sends a formatted Discord alert for a card listing.
    
    card: dict from load_cards + PSA/profit calculations
    listing: dict with 'title', 'price', 'url'
    """
    content = (
        f"**Card:** {card['card_name']}\n"
        f"**eBay Listing:** {listing['title']}\n"
        f"**eBay Price:** ${listing['price']:.2f}\n"
        f"**Market Average Price:** ${card['market_avg']:.2f}\n"
        f"**PSA 10 Price:** ${card['psa_10_price']:.2f}\n"
        f"**PSA 10 Profit:** ${card['psa_10_profit']:.2f}\n"
        f"**PSA 10 Profit Margin:** {card['psa_10_margin']:.2f}%\n"
        f"**PSA 9 Price:** ${card['psa_9_price']:.2f}\n"
        f"**PSA 9 Profit:** ${card['psa_9_profit']:.2f}\n"
        f"**PSA 9 Profit Margin:** {card['psa_9_margin']:.2f}%\n"
        f"**Velocity:** {card['velocity']}\n"
        f"**Link:** {listing['url']}"
    )

    async with aiohttp.ClientSession() as session:
        payload = {"content": content}
        try:
            async with session.post(DISCORD_WEBHOOK_URL, json=payload) as resp:
                if resp.status != 204 and resp.status != 200:
                    text = await resp.text()
                    print(f"[Discord] Failed to send alert: {resp.status} | {text}")
        except Exception as e:
            print(f"[Discord] Exception sending alert: {e}")
