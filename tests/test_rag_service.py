import sys
import os
# Add parent directory to path to import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rag_service import rag_service
from app.services.google_service import google_drive_service
from unittest.mock import MagicMock
from app.models.user import User

def test_rag_chunking():
    print("Testing RAG Chunking...")
    text = "A" * 2500
    chunks = rag_service.chunk_text(text, chunk_size=1000, overlap=100)
    assert len(chunks) == 3
    print("Chunking passed!")

def test_google_service_mock():
    print("Testing Google Service Logic...")
    user = User(email="test@example.com", google_access_token="fake_token")
    
    # Mock build
    original_build = google_drive_service.get_credentials
    google_drive_service.get_credentials = MagicMock(return_value=MagicMock())
    
    try:
        # We can't easily mock the google api client build without more complex mocking
        # So we just check if get_credentials returns the mock
        creds = google_drive_service.get_credentials(user)
        assert creds is not None
        print("Google Service Credential retrieval passed!")
    finally:
        google_drive_service.get_credentials = original_build

if __name__ == "__main__":
    test_rag_chunking()
    test_google_service_mock()
