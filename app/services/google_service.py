from typing import List, Optional
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User

class GoogleDriveService:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/drive.readonly']

    def get_credentials(self, user: User) -> Optional[Credentials]:
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
                # Update user tokens in DB (this requires a DB session, which we might need to pass or handle differently)
                # For now, we return the refreshed creds. The caller should ideally update the DB.
                # In a real app, we'd want to update the DB here.
            except Exception as e:
                print(f"Error refreshing token: {e}")
                return None
        
        return creds

    def list_files(self, user: User, limit: int = 10) -> List[dict]:
        creds = self.get_credentials(user)
        if not creds:
            raise Exception("User not authenticated with Google Drive")

        service = build('drive', 'v3', credentials=creds)
        
        # Query for Google Docs only for now
        results = service.files().list(
            q="mimeType='application/vnd.google-apps.document' and trashed=false",
            pageSize=limit,
            fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime)"
        ).execute()
        
        return results.get('files', [])

    def get_file_content(self, user: User, file_id: str) -> str:
        creds = self.get_credentials(user)
        if not creds:
            raise Exception("User not authenticated with Google Drive")

        service = build('drive', 'v3', credentials=creds)
        
        # Export Google Doc to plain text
        try:
            result = service.files().export_media(
                fileId=file_id,
                mimeType='text/plain'
            ).execute()
            return result.decode('utf-8')
        except Exception as e:
            print(f"Error getting file content: {e}")
            raise e

google_drive_service = GoogleDriveService()
