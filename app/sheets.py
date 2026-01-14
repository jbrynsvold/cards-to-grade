import os
import json
import gspread

GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
GOOGLE_SHEET_CARDS_NAME = os.environ.get("GOOGLE_SHEET_CARDS_NAME")

def parse_price(price_str):
    """Convert string like '$273.46' to float 273.46"""
    if not price_str:
        return 0.0
    return float(str(price_str).replace("$", "").replace(",", "").strip())

def load_cards():
    if not GOOGLE_SERVICE_ACCOUNT_JSON or not GOOGLE_SHEET_CARDS_NAME:
        raise ValueError("Google Sheets env vars not set")

    creds_dict = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    client = gspread.service_account_from_dict(creds_dict)
    sheet = client.open(GOOGLE_SHEET_CARDS_NAME).sheet1

    rows = sheet.get_all_records()
    cards = []
    for row in rows:
        try:
            cards.append({
                "card_name": row.get("card_name") or row.get("Name") or "",
                "player": row.get("player") or "",
                "set": row.get("set") or "",
                "card_number": row.get("card_number") or row.get("Card Number") or "",
                "parallel": row.get("parallel") or "",
                "sport": row.get("sport") or "",
                "market_avg": parse_price(row.get("Avg")),
                "psa_10_price": parse_price(row.get("PSA_10")),
                "psa_9_price": parse_price(row.get("PSA_9")),
                "velocity": float(row.get("velocity") or 0),
            })
        except Exception as e:
            print(f"[Sheets] Error parsing row: {row} | {e}")
            continue

    print(f"[Sheets] Loaded {len(cards)} cards from sheet.")
    return cards
