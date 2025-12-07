from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import engine
import httpx
from app.core.config import settings

class PgVectorStore:
    """
    Service for storing and retrieving document embeddings using Supabase pgvector.
    Replaces ChromaDB for persistent vector storage.
    """
    
    def __init__(self):
        self.hf_api_key = settings.HUGGINGFACE_API_KEY
        if not self.hf_api_key:
            print("WARNING: HUGGINGFACE_API_KEY is missing via settings!")
        # Using all-MiniLM-L6-v2 (384 dimensions) - reliable free tier model
        self.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text using Hugging Face Inference API"""
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.embedding_model}"
        
        response = httpx.post(api_url, headers=headers, json={"inputs": text})
        if response.status_code != 200:
            print(f"HF API Error: {response.status_code} - {response.text}")
        response.raise_for_status()
        
        # HF returns a list of embeddings (one per token), we take the mean
        embeddings = response.json()
        if isinstance(embeddings, list) and len(embeddings) > 0:
            # Mean pooling over all token embeddings
            return [sum(col) / len(embeddings) for col in zip(*embeddings)]
        return embeddings
    
    def index_document(self, user_id: int, content: str, source_metadata: Dict[str, Any]) -> None:
        """
        Index a document chunk by generating its embedding and storing in pgvector.
        
        Args:
            user_id: User ID for access control
            content: Text content to index
            source_metadata: Dict with 'source_app' and 'source_url'
        """
        try:
            # Generate embedding
            embedding = self._generate_embedding(content)
            
            # Insert into database
            with engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO document_embeddings 
                        (user_id, content, embedding, source_app, source_url)
                        VALUES (:user_id, :content, :embedding::vector, :source_app, :source_url)
                    """),
                    {
                        "user_id": user_id,
                        "content": content,
                        "embedding": str(embedding),  # pgvector accepts string representation
                        "source_app": source_metadata.get("source_app"),
                        "source_url": source_metadata.get("source_url")
                    }
                )
                conn.commit()
            print(f"Indexed document for user {user_id} from {source_metadata.get('source_app')}")
        except Exception as e:
            print(f"Error indexing document: {e}")
            raise
    
    def search(self, user_id: int, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query using vector similarity.
        
        Args:
            user_id: User ID to filter results
            query: Search query text
            top_k: Number of results to return
            
        Returns:
            List of dicts with 'content', 'source_app', 'source_url', 'similarity'
        """
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Search using cosine similarity
            with engine.connect() as conn:
                results = conn.execute(
                    text("""
                        SELECT 
                            content,
                            source_app,
                            source_url,
                            1 - (embedding <=> :query_embedding::vector) as similarity
                        FROM document_embeddings
                        WHERE user_id = :user_id
                        ORDER BY embedding <=> :query_embedding::vector
                        LIMIT :top_k
                    """),
                    {
                        "user_id": user_id,
                        "query_embedding": str(query_embedding),
                        "top_k": top_k
                    }
                ).fetchall()
                
                return [
                    {
                        "content": row[0],
                        "source_app": row[1],
                        "source_url": row[2],
                        "similarity": float(row[3])
                    }
                    for row in results
                ]
        except Exception as e:
            print(f"Error searching documents: {e}")
            raise
    
    def delete_user_documents(self, user_id: int, source_app: str = None) -> None:
        """
        Delete all documents for a user, optionally filtered by source app.
        
        Args:
            user_id: User ID
            source_app: Optional source app filter
        """
        try:
            with engine.connect() as conn:
                if source_app:
                    conn.execute(
                        text("DELETE FROM document_embeddings WHERE user_id = :user_id AND source_app = :source_app"),
                        {"user_id": user_id, "source_app": source_app}
                    )
                else:
                    conn.execute(
                        text("DELETE FROM document_embeddings WHERE user_id = :user_id"),
                        {"user_id": user_id}
                    )
                conn.commit()
            print(f"Deleted documents for user {user_id}" + (f" from {source_app}" if source_app else ""))
        except Exception as e:
            print(f"Error deleting documents: {e}")
            raise

# Singleton instance
pgvector_store = PgVectorStore()
