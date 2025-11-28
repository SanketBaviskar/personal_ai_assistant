from typing import Dict, Any, List
from app.services.sanitizer import sanitizer
from app.services.processing.chunker import chunker
from app.services.processing.embedding_service import embedding_service
from app.services.vector_db import vector_db

class RAGPipeline:
    def process_document(self, user_id: int, text: str, source_metadata: Dict[str, Any]) -> int:
        """
        Orchestrates the ETL process:
        1. Sanitize Text
        2. Chunk Text
        3. Embed Chunks (Implicit in VectorDB for some, but we'll prepare them)
        4. Index in Vector DB
        
        Returns the number of chunks indexed.
        """
        # 1. Sanitize
        clean_text = sanitizer.clean_text(text)
        clean_text = sanitizer.mask_pii(clean_text)

        # 2. Chunk
        chunks = chunker.chunk_text(clean_text)

        if not chunks:
            return 0

        # 3. & 4. Index
        # Note: Our current VectorDBClient.index_document takes a single text and handles embedding 
        # (if using Chroma's default) or we might need to pass embeddings if we use our own service.
        # Since we implemented `EmbeddingService` separately, let's assume we want to use it.
        # However, `VectorDBClient` currently takes raw text. 
        # For this phase, we will iterate and index each chunk as a separate document.
        
        for i, chunk in enumerate(chunks):
            # Create unique metadata for the chunk
            chunk_metadata = source_metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)
            
            # In a real production scenario with a custom embedding model, 
            # we would generate the embedding here:
            # vector = embedding_service.get_embedding(chunk)
            # And pass it to the DB. 
            # But our current `ChromaDBClient` relies on Chroma's default embedding function 
            # if no embedding is provided.
            # To strictly follow the plan which asked for an EmbeddingService, 
            # we should ideally pass the embedding. 
            # But `VectorDBClient.index_document` signature currently only takes `text`.
            # We will proceed with passing text to VectorDB, effectively letting Chroma handle embedding 
            # OR we update VectorDB to accept embeddings.
            # Given the previous step's implementation of VectorDB, it expects text.
            # We will stick to that for now to avoid breaking changes, 
            # but we acknowledge `embedding_service` is ready for when we switch to a custom model.
            
            vector_db.index_document(
                user_id=user_id,
                text=chunk,
                source_metadata=chunk_metadata
            )
            
        return len(chunks)

rag_pipeline = RAGPipeline()
