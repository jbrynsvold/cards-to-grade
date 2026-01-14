import aiohttp
import time
import base64
from urllib.parse import quote
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
        async with session.post(
            "https://api.ebay.com/identity/v1/oauth2/token",
            headers=headers,
            data=data
        ) as resp:
            resp_json = await resp.json()
            self.token = resp_json.get("access_token")
            self.token_expiry = time.time() + int(resp_json.get("expires_in", 3600)) - 60

    async def get_token(self, session):
        if not self.token or time.time() >= self.token_expiry:
            await self.refresh_token(session)
        return self.token

    async def search_listings(self, session, card, query_override=None):
        """
        Search eBay listings for a card.
        If query_override is provided, use that instead of Player+Set+Parallel.
        """
        token = await self.get_token(session)

        player = card.get("player", "")
        set_name = card.get("set", "")
        parallel = card.get("parallel", "")
        market_avg = card.get("market_avg", 0.0)

        # Use override query if provided
        query = query_override or f"{player} {set_name} {parallel}".strip()
        query_encoded = quote(query)

        # Filter: Buy It Now and optionally under market_avg
        filters = ["buyingOptions:FIXED_PRICE"]
        if market_avg > 0:
            filters.append(f"price:[0..{market_avg}]")

        filter_str = ",".join(filters)

        url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={query_encoded}&limit=10&filter={filter_str}"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": EBAY_MARKETPLACE_ID,
            "Content-Type": "application/json"
        }

        try:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                listings = data.get("itemSummaries", [])

                # Extra safety: remove any listings above market_avg
                filtered_listings = []
                for item in listings:
                    price_str = item.get("price", {}).get("value") or item.get("price", 0)
                    try:
                        price = float(price_str)
                    except:
                        price = 0.0
                    if price <= market_avg:
                        filtered_listings.append(item)

                # Fallback fuzzy: if nothing found, search Player + Set only
                if not filtered_listings and not query_override:
                    return await self.search_listings(session, card, query_override=f"{player} {set_name}")

                return filtered_listings
        except Exception as e:
            print(f"[eBay] Error searching listings for '{query}': {e}")
            return []
