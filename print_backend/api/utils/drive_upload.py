from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
import mimetypes
import io

def upload_file_to_drive(file):
    # Path to your service account JSON file
    SERVICE_ACCOUNT_FILE = "credentials.json"  # Make sure to use the correct path

    # Define the scope
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]  # Use drive.file for file uploads

    # Authenticate using the service account
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = build("drive", "v3", credentials=creds)

    # Get the file's name and MIME type
    file_name = file.name
    mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"

    # Define the folder ID where files should be uploaded
    folder_id = "1uozY6LfZBLXG7sSbkgD4Y66AjQWCLj81"  # Replace with your Google Drive Folder ID

    # Create file metadata
    file_metadata = {
        "name": file_name,  # The name of the file on Google Drive
        "parents": [folder_id]  # Upload inside this folder
    }

    # Use io.BytesIO to treat the file in memory as a file-like object
    file_stream = io.BytesIO(file.read())

    # Use MediaIoBaseUpload to handle the file upload
    media = MediaIoBaseUpload(file_stream, mimetype=mime_type)

    # Upload the file
    media_body = drive_service.files().create(
        body=file_metadata,
        media_body=media
    ).execute()

    # Return the uploaded file's ID
    return media_body["id"]
