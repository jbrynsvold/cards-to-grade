import aiohttp
import asyncio
from app.config import EBAY_APP_ID, EBAY_TOKEN, PSA10_PROFIT_THRESHOLD

# Simulate automatic refresh for token
async def refresh_ebay_token():
    # Implement refresh logic here
    # For example, POST to your refresh endpoint and update EBAY_TOKEN
    return EBAY_TOKEN

async def fetch_ebay_listings(card_name):
    token = await refresh_ebay_token()
    url = "https://svcs.ebay.com/services/search/FindingService/v1"
    params = {
        "OPERATION-NAME": "findItemsByKeywords",
        "SERVICE-VERSION": "1.0.0",
        "SECURITY-APPNAME": EBAY_APP_ID,
        "RESPONSE-DATA-FORMAT": "JSON",
        "keywords": card_name,
        "paginationInput.entriesPerPage": 10,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            items = data.get("findItemsByKeywordsResponse", [{}])[0]\
                        .get("searchResult", [{}])[0].get("item", [])
            results = []
            seen_titles = set()

            for item in items:
                title = item.get("title", [""])[0]
                price_str = item.get("sellingStatus", [{}])[0].get("currentPrice", [{}])[0].get("__value__", "0")
                try:
                    price = float(price_str)
                except:
                    price = 0.0

                if title in seen_titles:
                    continue
                seen_titles.add(title)

                if "PSA 10" in title.upper() and price > 0:
                    if price / 1.0 < PSA10_PROFIT_THRESHOLD / 100.0:
                        continue

                results.append({
                    "title": title,
                    "price": price,
                    "link": item.get("viewItemURL", [""])[0]
                })
            return results
