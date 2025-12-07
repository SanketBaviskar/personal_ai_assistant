from typing import List, Dict, Any
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
import io
try:
    from pypdf import PdfReader  # Updated package name
except ImportError:
    from PyPDF2 import PdfReader  # Fallback for older installations
from app.services.connectors.base import BaseConnector

class DriveConnector(BaseConnector):
    def fetch_data(self, credentials: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetches documents from Google Drive.
        Supports:
        - Google Docs (exported as plain text)
        - PDFs (text extracted)
        
        Args:
            credentials: Dict containing 'access_token' and 'refresh_token'
            
        Returns:
            List of dicts with 'text' and 'source_metadata'
        """
        access_token = credentials.get("access_token")
        refresh_token = credentials.get("refresh_token")
        
        if not access_token:
            raise ValueError("Missing Google Drive access token")
        
        # Build credentials object
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=credentials.get("client_id"),
            client_secret=credentials.get("client_secret")
        )
        
        # Build Drive API client
        service = build('drive', 'v3', credentials=creds)
        
        results = []
        
        # Query for Google Docs, PDFs, Images, and Word Docs
        query = "(mimeType='application/vnd.google-apps.document' or mimeType='application/pdf' or mimeType='image/jpeg' or mimeType='image/png' or mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document') and trashed=false"
        
        try:
            response = service.files().list(
                q=query,
                pageSize=10,  # Limit to 10 files per sync for now
                fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime)"
            ).execute()
            
            files = response.get('files', [])
            
            for file in files:
                file_id = file['id']
                file_name = file['name']
                mime_type = file['mimeType']
                
                try:
                    # Extract text based on file type
                    if mime_type == 'application/vnd.google-apps.document':
                        text = self._fetch_google_doc(service, file_id)
                    elif mime_type == 'application/pdf':
                        text = self._fetch_pdf(service, file_id)
                    elif mime_type in ['image/jpeg', 'image/png']:
                         text = self._fetch_image(service, file_id)
                    elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                         text = self._fetch_docx(service, file_id)
                    else:
                        continue
                    
                    if text:
                        results.append({
                            "text": text,
                            "source_metadata": {
                                "source_app": "google_drive",
                                "source_url": f"https://drive.google.com/file/d/{file_id}/view",
                                "file_name": file_name,
                                "mime_type": mime_type
                            }
                        })
                        print(f"Fetched: {file_name}")
                except Exception as e:
                    print(f"Error processing {file_name}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"Error fetching Drive files: {e}")
            raise
    
    def _fetch_google_doc(self, service, file_id: str) -> str:
        """Export Google Doc as plain text"""
        try:
            request = service.files().export_media(
                fileId=file_id,
                mimeType='text/plain'
            )
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                _, done = downloader.next_chunk()
            
            return file_content.getvalue().decode('utf-8')
        except Exception as e:
            print(f"Error exporting Google Doc {file_id}: {e}")
            return ""
    
    def _fetch_pdf(self, service, file_id: str) -> str:
        """Download and extract text from PDF"""
        try:
            request = service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                _, done = downloader.next_chunk()
            
            # Extract text using PyPDF2
            file_content.seek(0)
            pdf_reader = PdfReader(file_content)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting PDF {file_id}: {e}")
            return ""

    def _fetch_image(self, service, file_id: str) -> str:
        """Download and extract text from Image using OCR"""
        try:
            request = service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                _, done = downloader.next_chunk()
            
            from app.services.processing.image_processor import image_processor
            return image_processor.extract_text(file_content.getvalue())
        except Exception as e:
            print(f"Error extracting Image {file_id}: {e}")
            return ""

    def _fetch_docx(self, service, file_id: str) -> str:
        """Download and extract text from DOCX"""
        try:
            request = service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                _, done = downloader.next_chunk()
            
            from app.services.processing.docx_processor import docx_processor
            return docx_processor.extract_text(file_content.getvalue())
        except Exception as e:
            print(f"Error extracting DOCX {file_id}: {e}")
            return ""
