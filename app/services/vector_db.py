"""
Service for Vector Database operations.
Handles indexing and querying of documents using ChromaDB.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from app.core.config import settings

class VectorDBClient:
    """
    Abstract base class for Vector DB clients.
    """
    def index_document(self, user_id: int, text: str, source_metadata: Dict[str, Any]):
        raise NotImplementedError

    def query(self, user_id: int, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        raise NotImplementedError

class ChromaDBClient(VectorDBClient):
    """
    ChromaDB implementation of the VectorDBClient.
    """
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection(name="personal_knowledge_base")

    def index_document(self, user_id: int, text: str, source_metadata: Dict[str, Any]):
        """
        Indexes a single document with strict schema enforcement.

        Args:
            user_id (int): The ID of the user owning the document.
            text (str): The content of the document.
            source_metadata (Dict[str, Any]): Metadata associated with the document.
                Must contain 'source_app' and 'source_url'.
        """
        required_fields = ["source_app", "source_url"]
        for field in required_fields:
            if field not in source_metadata:
                raise ValueError(f"Missing required metadata field: {field}")

        metadata = source_metadata.copy()
        metadata["user_id"] = user_id
        
        import hashlib
        doc_id = hashlib.md5((text + str(user_id) + metadata["source_url"]).encode()).hexdigest()

        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def query(self, user_id: int, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Queries the vector database for relevant documents.

        Args:
            user_id (int): The ID of the user.
            query_text (str): The query string.
            n_results (int): Number of results to return.

        Returns:
            Dict[str, Any]: The query results.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where={"user_id": user_id}
        )
        return results

# Singleton instance
vector_db = ChromaDBClient()
