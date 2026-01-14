import gspread
from google.oauth2.service_account import Credentials
from app.config import GOOGLE_SHEET_CARDS_NAME, GOOGLE_SERVICE_ACCOUNT_JSON

def load_cards():
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_file(GOOGLE_SERVICE_ACCOUNT_JSON, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_CARDS_NAME).sheet1

    data = sheet.get_all_records()
    cards = []

    for row in data:
        try:
            market_avg = float(str(row.get("Avg") or "0").replace("$", "").replace(",", ""))
        except ValueError:
            market_avg = 0.0

        card = {
            "name": row.get("Card Name"),
            "set": row.get("Set"),
            "rarity": row.get("Rarity"),
            "market_avg": market_avg,
            "psa_grade": row.get("PSA Grade", None),
            "tcg_price": row.get("TCG Price", 0),
        }
        cards.append(card)

    print(f"[Sheets] Loaded {len(cards)} cards from sheet.")
    return cards
