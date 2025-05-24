

from dotenv import load_dotenv
import os
import json
from .client import GoogleDriveClient


class GoogleDriveClientFactory : 
    @staticmethod
    def from_env():
        load_dotenv()
        credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        parent_id = os.getenv("SHARED_FOLDER_ID")
        credentials_info = json.loads(credentials_json)
        return GoogleDriveClient(credentials_info , parent_id)