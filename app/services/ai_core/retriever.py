from typing import List, Dict, Any
from app.services.pgvector_store import pgvector_store

class Retriever:
    def retrieve_context(self, user_id: int, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves relevant context for a user query from the Vector DB.
        Enforces ACL by filtering on user_id.
        """
        # 1. Query Vector DB (pgvector handles embedding generation)
        results = pgvector_store.search(user_id=user_id, query=query, top_k=k)
        
        # 2. Format Results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "text": result["content"],
                "source_metadata": {
                    "source_app": result["source_app"],
                    "source_url": result["source_url"]
                },
                "similarity": result["similarity"]
            })
                
        return formatted_results

retriever = Retriever()
