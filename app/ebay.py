import aiohttp
import asyncio
import base64
import time
from app.config import EBAY_CLIENT_ID, EBAY_CLIENT_SECRET, EBAY_MARKETPLACE_ID

EBAY_TOKEN_CACHE = {"token": None, "expires_at": 0}

async def get_ebay_access_token():
    """Get eBay OAuth2 app access token (cached)."""
    now = int(time.time())
    if EBAY_TOKEN_CACHE["token"] and EBAY_TOKEN_CACHE["expires_at"] > now + 60:
        return EBAY_TOKEN_CACHE["token"]

    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + base64.b64encode(f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}".encode()).decode()
    }
    data = "grant_type=client_credentials&scope=https://api.ebay.com/oauth/api_scope"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"[eBay] Failed to get token: {resp.status} {text}")
            result = await resp.json()
            EBAY_TOKEN_CACHE["token"] = result["access_token"]
            EBAY_TOKEN_CACHE["expires_at"] = now + int(result.get("expires_in", 3600))
            return EBAY_TOKEN_CACHE["token"]

async def search_ebay_listings(session, card, limit=5):
    """
    Search eBay for a card.
    Returns a list of dicts with title, price, and URL.
    """
    access_token = await get_ebay_access_token()

    query_parts = [card.get("card_name", ""), card.get("set", "")]
    if card.get("parallel"):
        query_parts.append(card["parallel"])
    if card.get("player"):
        query_parts.append(card["player"])
    query = " ".join(query_parts)

    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={query}&limit={limit}&filter=buyingOptions:{'FIXED_PRICE'}&fieldgroups=PRODUCT"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-EBAY-C-MARKETPLACE-ID": EBAY_MARKETPLACE_ID
    }

    try:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                text = await resp.text()
                print(f"[eBay] Search failed: {resp.status} {text}")
                return []

            data = await resp.json()
            items = []
            for item in data.get("itemSummaries", []):
                price_info = item.get("price", {})
                items.append({
                    "title": item.get("title", ""),
                    "price": price_info,
                    "url": item.get("itemWebUrl")
                })
            return items

    except Exception as e:
        print(f"[eBay] Error searching eBay for {card.get('card_name')}: {e}")
        return []
