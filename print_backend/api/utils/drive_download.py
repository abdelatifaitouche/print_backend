from django.http import HttpResponse
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
import json

def download_file_from_google_drive(file_id):
    # Load the credentials from the JSON file

    try:
        load_dotenv()

        credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        credentials_info = json.loads(credentials_json)
        

        SERVICE_ACCOUNT_FILE = "credentials.json"  # Make sure to use the correct path

        # Define the scope
        SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]  # Use drive.file for file uploads

    # Authenticate using the service account
        creds = service_account.Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
        drive_service = build("drive", "v3", credentials=creds)
        # Get the file's metadata to retrieve the file name
        request = drive_service.files().get_media(fileId=file_id)
        file_handle = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handle, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        # Seek to the beginning of the file for downloading
        file_handle.seek(0)

        # Fetch the file's name (you can also use file metadata here)
        file_metadata = drive_service.files().get(fileId=file_id).execute()
        file_name = file_metadata['name']

        return file_name, file_handle

    except Exception as e:
        raise Exception(f"An error occurred while downloading the file: {str(e)}")
