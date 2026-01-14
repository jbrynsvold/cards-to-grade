import aiohttp
from app.config import DISCORD_WEBHOOK_URL

async def send_discord_alert(card, listing, url=None, listing_price=None):
    """Send a Discord alert for a card listing."""

    if not DISCORD_WEBHOOK_URL:
        print("[Discord] No webhook URL set, skipping alert.")
        return

    card_name = card.get("card_name", "Unknown Card")
    set_name = card.get("set", "")
    number = card.get("number", "")
    parallel = card.get("parallel", "")
    sport = card.get("sport", "")
    market_avg = card.get("market_avg", 0)
    velocity = card.get("velocity", 0)
    psa_10_price = card.get("psa_10_price", 0)
    psa_9_price = card.get("psa_9_price", 0)
    psa_10_profit = card.get("psa_10_profit", 0)
    psa_9_profit = card.get("psa_9_profit", 0)
    psa_10_margin = card.get("psa_10_margin", 0)
    psa_9_margin = card.get("psa_9_margin", 0)

    listing_title = listing.get("title", "No title")
    listing_price_str = f"${listing_price:.2f}" if listing_price else "N/A"
    url_str = url or "URL not available"

    message = (
        f"**Card:** {card_name} {set_name} #{number} {parallel}\n"
        f"**eBay Listing:** {listing_title}\n"
        f"**eBay Price:** {listing_price_str}\n"
        f"**Market Average Price:** ${market_avg:.2f}\n"
        f"**PSA 10 Price:** ${psa_10_price:.2f}\n"
        f"**PSA 10 Profit:** ${psa_10_profit:.2f}\n"
        f"**PSA 10 Profit Margin:** {psa_10_margin:.2f}%\n"
        f"**PSA 9 Price:** ${psa_9_price:.2f}\n"
        f"**PSA 9 Profit:** ${psa_9_profit:.2f}\n"
        f"**PSA 9 Profit Margin:** {psa_9_margin:.2f}%\n"
        f"**Velocity:** {velocity}\n"
        f"**Link:** {url_str}"
    )

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(DISCORD_WEBHOOK_URL, json={"content": message}) as resp:
                if resp.status != 204:
                    text = await resp.text()
                    print(f"[Discord] Failed to send alert: {resp.status} {text}")
        except Exception as e:
            print(f"[Discord] Error sending alert: {e}")
