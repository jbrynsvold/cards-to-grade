import aiohttp
from app.config import EBAY_APP_ID

EBAY_ENDPOINT = "https://api.ebay.com/buy/browse/v1/item_summary/search"


def build_query(card):
    base = f"{card['player']} {card['card']} {card['set']} {card['number']}"
    if card["parallel"]:
        base += f" {card['parallel']}"
    return base


async def search_ebay_listings(session, card):
    headers = {
        "X-EBAY-C-ENDUSERCTX": "contextualLocation=country=US",
        "Authorization": f"Bearer {EBAY_APP_ID}",
    }

    params = {
        "q": build_query(card),
        "limit": "10",
        "filter": "buyingOptions:{FIXED_PRICE},itemLocationCountry:US"
    }

    async with session.get(EBAY_ENDPOINT, headers=headers, params=params) as resp:
        if resp.status != 200:
            text = await resp.text()
            print(f"[eBay] {resp.status} {text}")
            return []

        data = await resp.json()
        return data.get("itemSummaries", [])


def extract_listing_url(listing):
    return (
        listing.get("itemWebUrl")
        or listing.get("itemUrl")
        or listing.get("viewItemURL")
        or "URL not available"
    )


def extract_price(listing):
    price = listing.get("price", {})
    if isinstance(price, dict):
        return float(price.get("value", 0))
    try:
        return float(price)
    except:
        return 0
