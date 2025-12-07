"""
Service for RAG (Retrieval-Augmented Generation) operations.
Handles text chunking, document ingestion, and querying.
"""
from typing import List, Dict, Any
from app.services.pgvector_store import pgvector_store
from app.models.user import User

try:
    from app.services.google_service import google_drive_service
except ImportError:
    google_drive_service = None

class RAGService:
    """
    Service class for RAG operations.
    """
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Splits text into overlapping chunks.
        """
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    def ingest_file(self, user: User, file_id: str, mime_type: str):
        """
        Fetches a file from Drive, processes it based on type, and indexes it.
        """
        if not google_drive_service:
            print("Google Drive Service not available")
            return

        try:
            content = google_drive_service.get_file_content(user, file_id, mime_type)
            
            text_to_index = ""
            
            if mime_type == 'application/vnd.google-apps.document':
                text_to_index = content
            elif mime_type == 'application/pdf':
                from app.services.processing.pdf_processor import pdf_processor
                text_to_index = pdf_processor.extract_text(content)
            elif mime_type in ['image/jpeg', 'image/png']:
                # Skipping image processing for now as requested
                return
            
            if not text_to_index:
                print(f"No text extracted for file {file_id} ({mime_type})")
                return

            chunks = self.chunk_text(text_to_index)
            
            for i, chunk in enumerate(chunks):
                metadata = {
                    "source_app": "google_drive",
                    "source_url": f"https://docs.google.com/document/d/{file_id}" if mime_type == 'application/vnd.google-apps.document' else f"drive://{file_id}",
                    "file_id": file_id,
                    "mime_type": mime_type,
                    "chunk_index": i
                }
                
                pgvector_store.index_document(user.id, chunk, metadata)
        except Exception as e:
            print(f"Error ingesting file {file_id}: {e}")

    def query(self, user_id: int, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Queries the Vector DB for relevant context.
        """
        return pgvector_store.search(user_id, query_text, top_k=k)

rag_service = RAGService()
