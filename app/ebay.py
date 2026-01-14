import aiohttp
from config import EBAY_APP_ID, PSA10_PROFIT_THRESHOLD

async def fetch_ebay_listings(card_name):
    url = f"https://svcs.ebay.com/services/search/FindingService/v1"
    params = {
        "OPERATION-NAME": "findItemsByKeywords",
        "SERVICE-VERSION": "1.0.0",
        "SECURITY-APPNAME": EBAY_APP_ID,
        "RESPONSE-DATA-FORMAT": "JSON",
        "keywords": card_name,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            items = data.get("findItemsByKeywordsResponse", [{}])[0].get("searchResult", [{}])[0].get("item", [])
            results = []
            seen_titles = set()

            for item in items:
                title = item.get("title", [""])[0]
                price_str = item.get("sellingStatus", [{}])[0].get("currentPrice", [{}])[0].get("__value__", "0")
                try:
                    price = float(price_str)
                except:
                    price = 0.0

                # Dedupe by title
                if title in seen_titles:
                    continue
                seen_titles.add(title)

                # PSA 10 profit check
                if "PSA 10" in title.upper() and price > 0:
                    if price / 1.0 < PSA10_PROFIT_THRESHOLD / 100.0:  # Example calculation
                        continue

                results.append({
                    "title": title,
                    "price": price,
                    "link": item.get("viewItemURL", [""])[0]
                })
            return results
