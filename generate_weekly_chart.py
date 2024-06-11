import requests
import pandas as pd
import matplotlib.pyplot as plt
import pytz
import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

# Configuration
HOME_ASSISTANT_URL = os.getenv("HOME_ASSISTANT_URL")
HOME_ASSISTANT_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN")
ENTITY_ID = os.getenv("ENTITY_ID")
BASE_DIR = os.getenv("BASE_DIR")
GOOGLE_CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
PLOTS_DIR = os.path.join(BASE_DIR, 'plots')
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

# Google Drive API setup
SCOPES = ['https://www.googleapis.com/auth/drive.file']
credentials = service_account.Credentials.from_service_account_file(
    GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)


def fetch_history():
    today = datetime.now()
    last_sunday = today - timedelta(days=today.weekday() + 1)
    last_monday = last_sunday - timedelta(days=6)

    start_time = last_monday.isoformat()
    end_time = last_sunday.isoformat()

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


def upload_to_drive(file_path):
    file_metadata = {'name': os.path.basename(file_path)}
    if DRIVE_FOLDER_ID:
        file_metadata['parents'] = [DRIVE_FOLDER_ID]
    media = MediaFileUpload(file_path, mimetype='image/png')
    file = service.files().create(body=file_metadata,
                                  media_body=media, fields='id').execute()
    print(f"File ID: {file.get('id')}")


def process_and_plot():
    # Fetch the history data
    history_data = fetch_history()

    # Flatten the JSON data and create a DataFrame
    df = pd.json_normalize(history_data[0])

    # Convert the 'last_changed' column to datetime format
    df['last_changed'] = pd.to_datetime(df['last_changed'])

    # Define the UTC and Pacific time zones
    pacific_zone = pytz.timezone('America/Los_Angeles')

    # Convert the 'last_changed' column to Pacific time
    df['last_changed_pacific'] = df['last_changed'].dt.tz_convert(pacific_zone)

    # Extract the hour in Pacific time
    df['hour_pacific'] = df['last_changed_pacific'].dt.hour

    # Filter the data to include only 'on' states
    activation_data_pacific = df[df['state'] == 'on']

    # Get the date range for the data
    start_date = df['last_changed_pacific'].dt.date.min()
    end_date = df['last_changed_pacific'].dt.date.max()
    date_range = f"{start_date} to {end_date}"

    # Plot the number of activations over the hours of the day for the full 24-hour period with thinner bins
    plt.figure(figsize=(14, 7))
    plt.hist(activation_data_pacific['hour_pacific'],
             bins=48, alpha=0.7, color='blue', label='Activations')
    plt.title(f'Garage Door Activations ({date_range})\n(Pacific Time)')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Number of Activations')
    plt.xticks(range(0, 24))
    plt.legend()
    plt.grid(True)

    # Generate a unique filename based on the current date and time
    output_file_name = f'GDA_{start_date}_to_{end_date}.png'
    output_file_path = os.path.join(PLOTS_DIR, output_file_name)

    # Save the plot as a PNG file
    plt.savefig(output_file_path)
    plt.show()

    # Upload the file to Google Drive
    upload_to_drive(output_file_path)

    # Delete the file from the local filesystem
    os.remove(output_file_path)


# Example usage
process_and_plot()
