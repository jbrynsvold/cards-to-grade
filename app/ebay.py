import aiohttp
import time
import base64
from app.config import EBAY_CLIENT_ID, EBAY_CLIENT_SECRET, EBAY_MARKETPLACE_ID

class EbayClient:
    def __init__(self):
        self.token = None
        self.token_expiry = 0

    async def refresh_token(self, session):
        auth = f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}"
        b64_auth = base64.b64encode(auth.encode()).decode()
        headers = {
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"}
        async with session.post("https://api.ebay.com/identity/v1/oauth2/token", headers=headers, data=data) as resp:
            resp_json = await resp.json()
            self.token = resp_json.get("access_token")
            self.token_expiry = time.time() + int(resp_json.get("expires_in", 3600)) - 60

    async def get_token(self, session):
        if not self.token or time.time() >= self.token_expiry:
            await self.refresh_token(session)
        return self.token

    async def search_listings(self, session, card):
        token = await self.get_token(session)
        query = f"{player} {set} {parallel}".strip()
        url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={query}&limit=5&filter=conditionIds:1000|1500"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": EBAY_MARKETPLACE_ID,
            "Content-Type": "application/json"
        }
        try:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                return data.get("itemSummaries", [])
        except Exception as e:
            print(f"[eBay] Error searching listings for {card['card_name']}: {e}")
            return []
