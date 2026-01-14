import os
import json
import gspread
from google.oauth2.service_account import Credentials
from app.config import GOOGLE_SERVICE_ACCOUNT_JSON, GOOGLE_SHEET_CARDS_NAME


def load_cards():
    if not GOOGLE_SERVICE_ACCOUNT_JSON:
        raise Exception("[Sheets] GOOGLE_SERVICE_ACCOUNT_JSON not set")

    creds_dict = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)

    scopes = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

    client = gspread.authorize(creds)

    sheet = client.open(GOOGLE_SHEET_CARDS_NAME).sheet1
    rows = sheet.get_all_records()

    cards = []

    for row in rows:
        cards.append({
            "card_name": row.get("Card"),
            "player": row.get("Player"),
            "set": row.get("Set"),
            "number": row.get("Number"),
            "parallel": row.get("Parallel"),
            "sport": row.get("Sport"),
            "market_avg": float(row.get("Avg") or 0),
            "velocity": float(row.get("Velocity") or 0),
            "psa10_price": float(row.get("PSA 10 Price") or 0),
            "psa9_price": float(row.get("PSA 9 Price") or 0),
        })

    return cards
