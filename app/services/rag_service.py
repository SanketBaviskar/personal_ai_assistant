"""
Service for RAG (Retrieval-Augmented Generation) operations.
Handles text chunking, document ingestion, and querying.
"""
from typing import List, Dict, Any
from app.services.vector_db import vector_db
from app.services.google_service import google_drive_service
from app.models.user import User

class RAGService:
    """
    Service class for RAG operations.
    """
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Splits text into overlapping chunks.

        Args:
            text (str): The input text to chunk.
            chunk_size (int): The maximum size of each chunk.
            overlap (int): The number of characters to overlap between chunks.

        Returns:
            List[str]: A list of text chunks.
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

        Args:
            user (User): The user performing the ingestion.
            file_id (str): The ID of the file to ingest.
            mime_type (str): The MIME type of the file.
        """
        try:
            content = google_drive_service.get_file_content(user, file_id, mime_type)
            
            text_to_index = ""
            
            if mime_type == 'application/vnd.google-apps.document':
                text_to_index = content
            elif mime_type == 'application/pdf':
                from app.services.processing.pdf_processor import pdf_processor
                text_to_index = pdf_processor.extract_text(content)
            elif mime_type in ['image/jpeg', 'image/png']:
                from app.services.processing.image_processor import image_processor
                text_to_index = image_processor.describe_image(content, mime_type)
            
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
                
                vector_db.index_document(user.id, chunk, metadata)
        except Exception as e:
            print(f"Error ingesting file {file_id}: {e}")

    def query(self, user_id: int, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Queries the Vector DB for relevant context.

        Args:
            user_id (int): The ID of the user.
            query_text (str): The query string.
            k (int): The number of results to return.

        Returns:
            List[Dict[str, Any]]: A list of relevant document chunks with metadata.
        """
        return vector_db.query(user_id, query_text, n_results=k)

rag_service = RAGService()
