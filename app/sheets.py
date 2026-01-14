import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from app.config import GOOGLE_SHEET_CARDS_NAME, GOOGLE_SERVICE_ACCOUNT_JSON

def parse_currency(value):
    """Convert $273.46 or 273.46 to float safely."""
    if not value:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    value_str = str(value).replace("$", "").replace(",", "").strip()
    try:
        return float(value_str)
    except Exception:
        return 0.0

def load_cards():
    """Load cards from Google Sheet and return a list of dicts."""
    if not GOOGLE_SERVICE_ACCOUNT_JSON:
        raise Exception("[Sheets] GOOGLE_SERVICE_ACCOUNT_JSON not set")

    creds_dict = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
    client = gspread.authorize(creds)

    sheet = client.open(GOOGLE_SHEET_CARDS_NAME).sheet1
    rows = sheet.get_all_records()

    cards = []
    seen = set()
    for row in rows:
        card_id = (
            row.get("Card", "") + "|" +
            row.get("Player", "") + "|" +
            row.get("Set", "") + "|" +
            str(row.get("Number", "")) + "|" +
            str(row.get("Parallel", ""))
        )
        if card_id in seen:
            continue
        seen.add(card_id)

        psa_10_price = parse_currency(row.get("PSA 10 Price"))
        psa_9_price = parse_currency(row.get("PSA 9 Price"))

        psa_10_profit = psa_10_price * 0.85 - 25
        psa_9_profit = psa_9_price * 0.85 - 25

        psa_10_margin = (psa_10_profit / 25) * 100 if psa_10_profit else 0
        psa_9_margin = (psa_9_profit / 25) * 100 if psa_9_profit else 0

        # Skip cards that don't meet PSA10 profit margin threshold
        if psa_10_margin < 100:
            continue

        card = {
            "card_name": row.get("Card", ""),
            "player": row.get("Player", ""),
            "set": row.get("Set", ""),
            "number": row.get("Number", ""),
            "parallel": row.get("Parallel", ""),
            "sport": row.get("Sport", ""),
            "market_avg": parse_currency(row.get("Avg")),
            "velocity": parse_currency(row.get("Velocity")),
            "psa_10_price": psa_10_price,
            "psa_9_price": psa_9_price,
            "psa_10_profit": psa_10_profit,
            "psa_9_profit": psa_9_profit,
            "psa_10_margin": psa_10_margin,
            "psa_9_margin": psa_9_margin
        }

        cards.append(card)

    print(f"[Sheets] Loaded {len(cards)} cards from Google Sheet.")
    return cards
