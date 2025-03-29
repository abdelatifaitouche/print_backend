from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path to your service account JSON file


def drive_auth():
    SERVICE_ACCOUNT_FILE = "credentials.json"
    print(SERVICE_ACCOUNT_FILE)

# Define the scope (Drive access)
    SCOPES = ["https://www.googleapis.com/auth/drive"]

# Authenticate with service account
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Connect to Google Drive API
    drive_service = build("drive", "v3", credentials=creds)

# List files in the shared Drive folder
    results = drive_service.files().list().execute()

# Print file names
    for file in results.get("files", []):
        print(f"{file['name']} ({file['id']})")
