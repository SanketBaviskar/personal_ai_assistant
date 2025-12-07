from typing import Dict, Any
from app.services.sanitizer import sanitizer
from app.services.processing.chunker import chunker
from app.services.pgvector_store import pgvector_store

class RAGPipeline:
    def process_document(self, user_id: int, text: str, source_metadata: Dict[str, Any]) -> int:
        """
        Orchestrates the ETL process:
        1. Sanitize Text
        2. Chunk Text
        3. Index in pgvector (which handles embedding generation)
        
        Returns the number of chunks indexed.
        """
        # 1. Sanitize
        clean_text = sanitizer.clean_text(text)
        clean_text = sanitizer.mask_pii(clean_text)

        # 2. Chunk
        chunks = chunker.chunk_text(clean_text)

        if not chunks:
            return 0

        # 3. Index each chunk in pgvector
        for chunk in chunks:
            pgvector_store.index_document(
                user_id=user_id,
                content=chunk,
                source_metadata=source_metadata
            )
            
        return len(chunks)

rag_pipeline = RAGPipeline()
