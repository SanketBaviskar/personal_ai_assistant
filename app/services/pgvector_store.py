from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import engine
import httpx
import json
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
        # Using BAAI/bge-small-en-v1.5 (384 dimensions) - High performance & free
        self.embedding_model = "BAAI/bge-small-en-v1.5"
    
    def _generate_embedding(self, text: str, instruction: str = "") -> List[float]:
        """Generate embedding vector for text using Hugging Face Inference API"""
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        # Correct URL for the new HF Inference Router
        api_url = f"https://router.huggingface.co/hf-inference/models/{self.embedding_model}"
        
        # Prepend instruction if provided (Critical for BGE models on query side)
        input_text = f"{instruction}{text}"
        
        # Retry logic for 500/503 errors
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Increased timeout to 30s for free tier cold starts
                response = httpx.post(api_url, headers=headers, json={"inputs": input_text}, timeout=30.0)
                
                if response.status_code == 503:
                    print(f"HF Model loading (503), retrying in {2 ** attempt}s...")
                    time.sleep(2 ** attempt)
                    continue
                    
                if response.status_code == 500:
                    print(f"HF Server Error (500), retrying in {2 ** attempt}s...")
                    time.sleep(2 ** attempt)
                    continue
                    
                if response.status_code != 200:
                    print(f"HF API Error: {response.status_code} - {response.text}")
                    response.raise_for_status()
                    
                # Success
                break
            except httpx.TimeoutException:
                print(f"HF Timeout, retrying in {2 ** attempt}s...")
                time.sleep(2 ** attempt)
                continue
        else:
             raise Exception(f"Failed to generate embedding after {max_retries} attempts")
        
        response.raise_for_status()
        
        embeddings = response.json()
        
        # Handle different response formats
        if isinstance(embeddings, list):
            if len(embeddings) == 0:
                return []
                
            # Case 1: 1D list of floats (Direct embedding) - BGE models often return this for single input
            if isinstance(embeddings[0], float):
                return embeddings
                
            # Case 2: List of lists (Batch of 1 or Token embeddings)
            if isinstance(embeddings[0], list):
                # If it's a batch of 1 (which gives [[float, float...]]), take the first one
                if isinstance(embeddings[0][0], float):
                    return embeddings[0]
                    
                # Case 3: Token embeddings (List[List[float]]) - Mean pool
                # This logic remains for models that return token embeddings
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
                        (user_id, content, embedding, source_app, source_url, metadata)
                        VALUES (:user_id, :content, CAST(:embedding AS vector), :source_app, :source_url, :metadata)
                    """),
                    {
                        "user_id": user_id,
                        "content": content,
                        "embedding": str(embedding),  # pgvector accepts string representation
                        "source_app": source_metadata.get("source_app"),
                        "source_url": source_metadata.get("source_url"),
                        "metadata": json.dumps(source_metadata) # Store full metadata as JSON
                    }
                )
                conn.commit()
            print(f"Indexed document for user {user_id} from {source_metadata.get('source_app')}")
        except Exception as e:
            print(f"Error indexing document: {e}")
            raise
    
    def search(self, user_id: int, query: str, top_k: int = 5, conversation_id: int = None) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query using vector similarity.
        Supports filtering by conversation_id (scoped search).
        """
        try:
            # Generate query embedding
            instruction = "Represent this sentence for searching relevant passages: "
            query_embedding = self._generate_embedding(query, instruction)
            
            # Search using cosine similarity
            # Logic: (user_id match) AND (conv_id match OR conv_id is null/global)
            filter_clause = "user_id = :user_id"
            params = {
                "user_id": user_id,
                "query_embedding": str(query_embedding),
                "top_k": top_k
            }
            
            if conversation_id:
                filter_clause += " AND (metadata->>'conversation_id' IS NULL OR metadata->>'conversation_id' = :conv_id)"
                params["conv_id"] = str(conversation_id)
            else:
                # If no conversation context, maybe only show global? Or all?
                # Usually if no context, we show all user's files.
                pass 

            with engine.connect() as conn:
                results = conn.execute(
                    text(f"""
                        SELECT 
                            content,
                            source_app,
                            source_url,
                            1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
                        FROM document_embeddings
                        WHERE {filter_clause}
                        ORDER BY embedding <=> CAST(:query_embedding AS vector)
                        LIMIT :top_k
                    """),
                    params
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
    
    def delete_document_by_file_id(self, user_id: int, file_id: str) -> None:
        """
        Delete a specific document (and all its chunks) by file_id.
        """
        try:
            with engine.connect() as conn:
                conn.execute(
                    text("DELETE FROM document_embeddings WHERE user_id = :user_id AND metadata->>'file_id' = :file_id"),
                    {"user_id": user_id, "file_id": file_id}
                )
                conn.commit()
            print(f"Deleted document {file_id} for user {user_id}")
        except Exception as e:
            print(f"Error deleting document {file_id}: {e}")
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

    def get_user_file_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get statistics about a user's uploaded files.
        """
        try:
            with engine.connect() as conn:
                # Get distinct file names from metadata
                # Using COALESCE to fallback to source_url if file_name is missing
                result = conn.execute(
                    text("""
                        SELECT 
                            COUNT(DISTINCT metadata->>'file_id') as file_count,
                            STRING_AGG(DISTINCT metadata->>'file_name', ', ') as file_list,
                            COUNT(*) as chunk_count
                        FROM document_embeddings
                        WHERE user_id = :user_id
                    """),
                    {"user_id": user_id}
                ).fetchone()
                
                return {
                    "file_count": result[0],
                    "file_names": result[1] if result[1] else "(No files found)",
                    "total_chunks": result[2]
                }
        except Exception as e:
            print(f"Error getting file stats: {e}")
            return {"file_count": 0, "file_names": "", "total_chunks": 0}

    def has_document(self, user_id: int, file_id: str) -> bool:
        """
        Check if a document with the given file_id already exists for the user.
        """
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT 1 
                        FROM document_embeddings 
                        WHERE user_id = :user_id 
                        AND metadata->>'file_id' = :file_id
                        LIMIT 1
                    """),
                    {"user_id": user_id, "file_id": file_id}
                ).fetchone()
                return result is not None
        except Exception as e:
            print(f"Error checking document existence: {e}")
            return False

# Singleton instance
pgvector_store = PgVectorStore()
