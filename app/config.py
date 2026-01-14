import os
from dotenv import load_dotenv

load_dotenv()

# Google Sheet
GOOGLE_SHEET_CARDS_NAME = os.getenv("GOOGLE_SHEET_CARDS_NAME")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

# eBay
EBAY_APP_ID = os.getenv("EBAY_APP_ID")
EBAY_SITE_ID = "0"  # US
EBAY_CONDITION_NEW = 1000  # Example: for cards

# Discord
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Bot settings
CONCURRENT_EBAY_REQUESTS = int(os.getenv("CONCURRENT_EBAY_REQUESTS", 10))
PSA10_PROFIT_THRESHOLD = float(os.getenv("PSA10_PROFIT_THRESHOLD", 100))  # in %
