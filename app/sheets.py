import json
import gspread
from google.oauth2.service_account import Credentials
from app.config import GOOGLE_SERVICE_ACCOUNT_JSON, GOOGLE_SHEET_CARDS_NAME


def load_cards():
    if not GOOGLE_SERVICE_ACCOUNT_JSON:
        raise Exception("GOOGLE_SERVICE_ACCOUNT_JSON not set")

    if not GOOGLE_SHEET_CARDS_NAME:
        raise Exception("GOOGLE_SHEET_CARDS_NAME not set")

    creds_dict = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly"
    ]

    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)

    sheet = client.open(GOOGLE_SHEET_CARDS_NAME).sheet1
    rows = sheet.get_all_records()

    print(f"[Sheets] Loaded {len(rows)} cards")

    cards = []

    for idx, row in enumerate(rows, start=1):
        try:
            def f(val):
                return float(str(val).replace("$", "").replace(",", "").strip() or 0)

            def i(val):
                return int(val or 0)

            card = {
                "card": str(row.get("Card", "")).strip(),
                "player": str(row.get("Player", "")).strip(),
                "set": str(row.get("Set", "")).strip(),
                "number": str(row.get("Number", "")).strip(),
                "parallel": str(row.get("Parallel", "")).strip(),
                "grade": str(row.get("Grade", "")).strip(),
                "sport": str(row.get("Sport", "")).strip(),

                "last_sale": f(row.get("Last Sale")),
                "avg": f(row.get("Avg")),
                "velocity": i(row.get("Velocity")),

                "psa10_price": f(row.get("PSA 10 Price")),
                "psa9_price": f(row.get("PSA 9 Price")),
                "psa10_profit": f(row.get("PSA 10 Profit")),
                "psa9_profit": f(row.get("PSA 9 Profit")),
            }

            if card["avg"] > 0:
                cards.append(card)

        except Exception as e:
            print(f"[Sheets] Skipping row {idx}: {e}")

    print(f"[Sheets] Final cards loaded: {len(cards)}")
    return cards
