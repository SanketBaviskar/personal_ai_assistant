from typing import List, Dict, Any
from app.services.pgvector_store import pgvector_store

class Retriever:
    async def retrieve_context(self, user_id: int, query: str, k: int = 5, conversation_id: int = None) -> Dict[str, Any]:
        """
        Retrieves context and metadata stats.
        Returns: { 'chunks': [...], 'stats': {...} }
        """
        # 1. Query Vector DB (pgvector handles embedding generation)
        results = await pgvector_store.search(user_id=user_id, query=query, top_k=k, conversation_id=conversation_id)
        
        # 2. Get Stats (Metadata Awareness)
        from starlette.concurrency import run_in_threadpool
        stats = await run_in_threadpool(pgvector_store.get_user_file_stats, user_id)
        
        # 3. Format Results
        formatted_chunks = []
        for result in results:
            formatted_chunks.append({
                "text": result["content"],
                "source_metadata": {
                    "source_app": result["source_app"],
                    "source_url": result["source_url"]
                },
                "similarity": result["similarity"]
            })
                
        return {
            "chunks": formatted_chunks,
            "stats": stats
        }

retriever = Retriever()
