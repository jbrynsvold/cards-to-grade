import aiohttp
import asyncio
import base64
import time

from app.config import (
    EBAY_CLIENT_ID,
    EBAY_CLIENT_SECRET,
    EBAY_MARKETPLACE_ID
)

TOKEN_CACHE = {
    "access_token": None,
    "expires_at": 0
}

EBAY_TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"


async def get_access_token(session: aiohttp.ClientSession) -> str:
    now = time.time()

    if TOKEN_CACHE["access_token"] and now < TOKEN_CACHE["expires_at"]:
        return TOKEN_CACHE["access_token"]

    credentials = f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }

    async with session.post(EBAY_TOKEN_URL, headers=headers, data=data) as resp:
        result = await resp.json()

        if "access_token" not in result:
            raise Exception(f"Failed to get token: {result}")

        TOKEN_CACHE["access_token"] = result["access_token"]
        TOKEN_CACHE["expires_at"] = now + result.get("expires_in", 7200) - 60

        return TOKEN_CACHE["access_token"]


async def search_ebay_listings(session: aiohttp.ClientSession, card: dict):
    try:
        token = await get_access_token(session)

        query = f"{card['card_name']} {card.get('set', '')} {card.get('card_number', '')}"

        headers = {
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": EBAY_MARKETPLACE_ID
        }

        params = {
            "q": query,
            "limit": "10",
            "filter": "buyingOptions:{FIXED_PRICE}"
        }

        async with session.get(EBAY_SEARCH_URL, headers=headers, params=params) as resp:
            if resp.status == 429:
                print("[eBay] Rate limited (429)")
                return []

            if resp.status != 200:
                text = await resp.text()
                print(f"[eBay] Search failed {resp.status}: {text}")
                return []

            data = await resp.json()
            items = data.get("itemSummaries", [])

            listings = []
            for item in items:
                listings.append({
                    "title": item.get("title"),
                    "price": item.get("price"),
                    "url": item.get("itemWebUrl")
                })

            return listings

    except Exception as e:
        print(f"[eBay] Error: {e}")
        return []
