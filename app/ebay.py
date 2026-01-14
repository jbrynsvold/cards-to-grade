import os
import aiohttp
import base64

EBAY_CLIENT_ID = os.environ.get("EBAY_CLIENT_ID")
EBAY_CLIENT_SECRET = os.environ.get("EBAY_CLIENT_SECRET")
EBAY_MARKETPLACE_ID = os.environ.get("EBAY_MARKETPLACE_ID") or "EBAY_US"

EBAY_TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_FINDING_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"

class EbayAPI:
    def __init__(self):
        self.access_token = None

    async def refresh_token(self, session):
        auth = base64.b64encode(f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}".encode()).decode()
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Basic {auth}"}
        data = {"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"}
        async with session.post(EBAY_TOKEN_URL, headers=headers, data=data) as resp:
            resp_json = await resp.json()
            self.access_token = resp_json.get("access_token")

    async def search(self, session, query):
        if not self.access_token:
            await self.refresh_token(session)
        params = {
            "q": query,
            "limit": 5,
            "filter": f"priceCurrency:USD,marketplaceId:{EBAY_MARKETPLACE_ID}"
        }
        headers = {"Authorization": f"Bearer {self.access_token}"}
        async with session.get(EBAY_FINDING_URL, headers=headers, params=params) as resp:
            return await resp.json()

ebay_api = EbayAPI()

async def search_ebay_listings(session, card):
    query = f"{card['player']} {card['set']} {card['card_name']} {card['parallel']}".strip()
    results = await ebay_api.search(session, query)
    items = results.get("itemSummaries", [])
    listings = []
    for item in items:
        listings.append({
            "title": item.get("title"),
            "price": float(item["price"]["value"]),
            "url": item.get("itemWebUrl")
        })
    return listings
