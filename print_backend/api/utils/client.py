from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
import mimetypes
import io
import os
import json
from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from googleapiclient.http import MediaIoBaseDownload



class GoogleDriveClient : 
    def __init__(self , credentials_info , main_parent_id : str):
        if not credentials_info : 
            raise Exception("No credentials were set for the client")
        
        self.creds = service_account.Credentials.from_service_account_info(
            credentials_info , 
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        self.parent_id = main_parent_id
        self.service = build("drive" , "v3" , credentials=self.creds)
                    
        
    def upload_file_to_drive(self , file , folder : dict):  
        #print('folder at upload to drive' , folder)      
        # Get the file's name and MIME type
        file_name = file.name
        mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"

        # Define the folder ID where files should be uploaded
        #folder_id = "1uozY6LfZBLXG7sSbkgD4Y66AjQWCLj81"  # Replace with your Google Drive Folder ID

        # Create file metadata
        file_metadata = {
            "name": file_name,  # The name of the file on Google Drive
            "parents": [self.get_or_create_folder(folder, self.parent_id)]  # Upload inside this folder
        }

        # Use io.BytesIO to treat the file in memory as a file-like object
        file_stream = io.BytesIO(file.read())

        # Use MediaIoBaseUpload to handle the file upload
        media = MediaIoBaseUpload(file_stream, mimetype=mime_type)

        # Upload the file
        media_body = self.service.files().create(
            body=file_metadata,
            media_body=media
        ).execute()

        # Return the uploaded file's ID
        return media_body["id"]
    
    def create_folder(self , folder_name, parent_id=None):
        # Define folder metadata
        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }

        if parent_id:
            folder_metadata["parents"] = [parent_id]

        try:
            folder = self.service.files().create(
                body=folder_metadata,
                fields="id, name"
            ).execute()

            print(f"Folder '{folder['name']}' created with ID: {folder['id']}")
            return folder['id']

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def get_folder_by_name(self, folder_name: str) -> dict:

        parent_id = self.parent_id
        query = (
            f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' "
            f"and name='{folder_name}' and trashed=false"
        )

        try:
            response = self.service.files().list(
                q=query,
                spaces="drive",
                fields="files(id, name)",
            ).execute()

            folders = response.get("files", [])
            return folders[0] if folders else None

        except HttpError as error:
            raise RuntimeError(f"Google Drive API error during folder search: {error}")
    
    def get_or_create_folder(self , folder_name : str , parent_id : str = None) -> dict:
        folder = self.get_folder_by_name(folder_name)
        if folder is not None : 
            return folder['id']
        
        return self.create_folder(folder_name , parent_id)
    
    
    def download_file_from_google_drive(self , file_id):
        # Load the credentials from the JSON file

        try:
        # Authenticate using the service account
        # Get the file's metadata to retrieve the file name
            request = self.service.files().get_media(fileId=file_id)
            file_handle = io.BytesIO()
            downloader = MediaIoBaseDownload(file_handle, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()

        # Seek to the beginning of the file for downloading
            file_handle.seek(0)

        # Fetch the file's name (you can also use file metadata here)
            file_metadata = self.service.files().get(fileId=file_id).execute()
            file_name = file_metadata['name']

            return file_name, file_handle

        except Exception as e:
            raise Exception(f"An error occurred while downloading the file: {str(e)}")
