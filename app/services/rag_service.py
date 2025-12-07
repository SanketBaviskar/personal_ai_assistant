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

from app.services.processing.chunker import chunker

class RAGService:
    """
    Service class for RAG operations.
    """

    async def ingest_file(self, user: User, file_id: str, mime_type: str, file_name: str = None):
        """
        Fetches a file from Drive, processes it based on type, and indexes it (Async).
        """
        if not google_drive_service:
            print("Google Drive Service not available")
            return

        try:
            from starlette.concurrency import run_in_threadpool
            
            # Blocking Drive API Call -> Thread
            content = await run_in_threadpool(google_drive_service.get_file_content, user, file_id, mime_type)
            
            text_to_index = ""
            
            # Blocking CPU tasks -> Thread
            if mime_type == 'application/vnd.google-apps.document':
                text_to_index = content
            elif mime_type == 'application/pdf':
                from app.services.processing.pdf_processor import pdf_processor
                text_to_index = await run_in_threadpool(pdf_processor.extract_text, content)
            elif mime_type in ['image/jpeg', 'image/png']:
                from app.services.processing.image_processor import image_processor
                text_to_index = await run_in_threadpool(image_processor.extract_text, content)
            elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                from app.services.processing.docx_processor import docx_processor
                text_to_index = await run_in_threadpool(docx_processor.extract_text, content)
            
            if not text_to_index:
                print(f"No text extracted for file {file_id} ({mime_type})")
                return

            # Blocking CPU task -> Thread
            chunks = await run_in_threadpool(chunker.chunk_text, text_to_index)
            
            for i, chunk in enumerate(chunks):
                metadata = {
                    "source_app": "google_drive",
                    "source_url": f"https://docs.google.com/document/d/{file_id}" if mime_type == 'application/vnd.google-apps.document' else f"drive://{file_id}",
                    "file_id": file_id,
                    "mime_type": mime_type,
                    "file_name": file_name,
                    "chunk_index": i
                }
                
                # Async Vector Store Call
                await pgvector_store.index_document(user.id, chunk, metadata)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error ingesting file {file_id}: {e}")

    async def query(self, user_id: int, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Queries the Vector DB for relevant context (Async).
        """
        return await pgvector_store.search(user_id, query_text, top_k=k)

rag_service = RAGService()
