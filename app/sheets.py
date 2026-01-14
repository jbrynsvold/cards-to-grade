import gspread
from google.oauth2.service_account import Credentials
from app.config import GOOGLE_SHEET_CARDS_NAME, GOOGLE_SERVICE_ACCOUNT_JSON

def load_cards():
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_info(GOOGLE_SERVICE_ACCOUNT_JSON, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_CARDS_NAME).sheet1

    data = sheet.get_all_records()
    cards = []

    for row in data:
        def parse_float(value):
            try:
                return float(str(value).replace("$", "").replace(",", "").strip())
            except:
                return 0.0

        card_name = row.get("Card")
        card_set = row.get("Set")

        # Skip any rows missing required info
        if not card_name or not card_set:
            continue

        card = {
            "card_name": card_name,
            "player": row.get("Player"),
            "set": card_set,
            "card_number": row.get("Number"),
            "parallel": row.get("Parallel"),
            "sport": row.get("Sport"),
            "market_avg": parse_float(row.get("Avg")),
            "psa_10_price": parse_float(row.get("PSA 10 Price")),
            "psa_9_price": parse_float(row.get("PSA 9 Price")),
            "velocity": parse_float(row.get("Velocity")),
            "tcg_price": parse_float(row.get("Last Sale")),  # optional, if needed
        }
        cards.append(card)

    print(f"[Sheets] Loaded {len(cards)} cards from sheet.")
    return cards
