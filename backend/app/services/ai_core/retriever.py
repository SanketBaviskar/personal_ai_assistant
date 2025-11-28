from typing import List, Dict, Any
from app.services.vector_db import vector_db
from app.services.processing.embedding_service import embedding_service

class Retriever:
    def retrieve_context(self, user_id: int, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves relevant context for a user query from the Vector DB.
        Enforces ACL by filtering on user_id.
        """
        # 1. Embed Query
        # Note: Our current VectorDBClient.query takes raw text and handles embedding 
        # (if using Chroma's default) or we might need to pass embeddings.
        # Similar to RAGPipeline, we will stick to passing text for now to match VectorDB implementation.
        # Ideally, we would do: query_vector = embedding_service.get_embedding(query)
        
        # 2. Query Vector DB
        results = vector_db.query(user_id=user_id, query_text=query, n_results=k)
        
        # 3. Format Results
        formatted_results = []
        if results and results['documents']:
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            
            for i, doc in enumerate(documents):
                formatted_results.append({
                    "text": doc,
                    "source_metadata": metadatas[i]
                })
                
        return formatted_results

retriever = Retriever()
