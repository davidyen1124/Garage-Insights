import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Configuration
HOME_ASSISTANT_URL = os.getenv("HOME_ASSISTANT_URL")
HOME_ASSISTANT_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN")
ENTITY_ID = os.getenv("ENTITY_ID")
BASE_DIR = os.getenv("BASE_DIR")
GOOGLE_CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = service_account.Credentials.from_service_account_file(
    GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()


def fetch_history():
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)

    # Format to ISO 8601 with 'Z' indicating UTC
    start_time = start_time.isoformat() + 'Z'
    end_time = end_time.isoformat() + 'Z'

    url = f"{HOME_ASSISTANT_URL}/api/history/period/{start_time}"
    headers = {
        "Authorization": f"Bearer {HOME_ASSISTANT_TOKEN}",
        "Content-Type": "application/json",
    }
    params = {
        "filter_entity_id": ENTITY_ID,
        "end_time": end_time,
        "minimal_response": "true",
        "no_attributes": "true",
        "significant_changes_only": "true"
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    # Return the JSON response
    return response.json()


def append_to_spreadsheet(data):
    # Convert the 'last_changed' column to datetime format in UTC
    data['last_changed'] = pd.to_datetime(
        data['last_changed']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Filter the data to include only 'on' states
    activation_data_utc = data[data['state'] == 'on'].copy()

    # Prepare the data to append
    values = activation_data_utc[['last_changed']].values.tolist()

    # Append the data to the spreadsheet, starting from the second row
    body = {
        'values': values
    }
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Sheet1!A2",  # Change this to A2 to start appending from the second row
        valueInputOption="RAW",
        body=body
    ).execute()
    print(f"{result.get('updates').get('updatedCells')} cells appended.")


def process_and_append():
    # Fetch the history data
    history_data = fetch_history()

    # Flatten the JSON data and create a DataFrame
    df = pd.json_normalize(history_data[0])

    # Append the data to the spreadsheet
    append_to_spreadsheet(df)


# Example usage
process_and_append()
