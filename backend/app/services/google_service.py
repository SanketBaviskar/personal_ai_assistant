"""
Service for interacting with Google Drive API.
Handles authentication, file listing, and content retrieval.
"""
from typing import List, Optional, Any, Union
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User

class GoogleDriveService:
    """
    Service class for Google Drive operations.
    """
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/drive.readonly']

    def get_credentials(self, user: User) -> Optional[Credentials]:
        """
        Retrieves and refreshes Google OAuth credentials for a user.

        Args:
            user (User): The user object containing OAuth tokens.

        Returns:
            Optional[Credentials]: Valid Google Credentials object or None.
        """
        if not user.google_access_token:
            return None
        
        creds = Credentials(
            token=user.google_access_token,
            refresh_token=user.google_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=self.scopes
        )

        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                return None
        
        return creds

    def list_files(self, user: User, limit: int = 10) -> List[dict]:
        """
        Lists Google Docs files from the user's Drive.

        Args:
            user (User): The user to list files for.
            limit (int): Maximum number of files to return.

        Returns:
            List[dict]: List of file metadata objects.
        """
        creds = self.get_credentials(user)
        if not creds:
            raise Exception("User not authenticated with Google Drive")

        service = build('drive', 'v3', credentials=creds)
        
        results = service.files().list(
            q="(mimeType='application/vnd.google-apps.document' or mimeType='application/pdf' or mimeType='image/jpeg' or mimeType='image/png') and trashed=false",
            pageSize=limit,
            fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime)"
        ).execute()
        
        return results.get('files', [])

    def get_file_content(self, user: User, file_id: str, mime_type: str = 'application/vnd.google-apps.document') -> Any:
        """
        Exports a Google Doc to plain text or downloads binary content.

        Args:
            user (User): The user requesting the file.
            file_id (str): The ID of the file to retrieve.
            mime_type (str): The MIME type of the file.

        Returns:
            Union[str, bytes]: The content of the file.
        """
        creds = self.get_credentials(user)
        if not creds:
            raise Exception("User not authenticated with Google Drive")

        service = build('drive', 'v3', credentials=creds)
        
        try:
            if mime_type == 'application/vnd.google-apps.document':
                result = service.files().export_media(
                    fileId=file_id,
                    mimeType='text/plain'
                ).execute()
                return result.decode('utf-8')
            else:
                # Binary download for PDF, Images, etc.
                result = service.files().get_media(fileId=file_id).execute()
                return result
        except Exception as e:
            print(f"Error getting file content: {e}")
            raise e

google_drive_service = GoogleDriveService()
