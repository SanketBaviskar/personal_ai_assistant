from typing import List, Dict, Any
from app.services.vector_db import vector_db
from app.services.google_service import google_drive_service
from app.models.user import User

class RAGService:
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Simple text chunking.
        """
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    def ingest_google_doc(self, user: User, file_id: str):
        """
        Fetches a Google Doc, chunks it, and indexes it in the Vector DB.
        """
        # 1. Fetch content
        content = google_drive_service.get_file_content(user, file_id)
        
        # 2. Chunk content
        chunks = self.chunk_text(content)
        
        # 3. Index chunks
        for i, chunk in enumerate(chunks):
            metadata = {
                "source_app": "google_drive",
                "source_url": f"https://docs.google.com/document/d/{file_id}",
                "file_id": file_id,
                "chunk_index": i
            }
            # We might want to include file name in metadata, but we'd need to fetch it separately or pass it in.
            # For now, we'll skip it or fetch it if needed.
            
            vector_db.index_document(user.id, chunk, metadata)

    def query(self, user_id: int, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Queries the Vector DB.
        """
        return vector_db.query(user_id, query_text, n_results=k)

rag_service = RAGService()
