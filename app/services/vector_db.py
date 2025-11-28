import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from app.core.config import settings

class VectorDBClient:
    def index_document(self, user_id: int, text: str, source_metadata: Dict[str, Any]):
        raise NotImplementedError

    def query(self, user_id: int, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        raise NotImplementedError

class ChromaDBClient(VectorDBClient):
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection(name="personal_knowledge_base")

    def index_document(self, user_id: int, text: str, source_metadata: Dict[str, Any]):
        """
        Indexes a single document with strict schema enforcement.
        source_metadata must contain 'source_app' and 'source_url'.
        """
        # Schema Validation
        required_fields = ["source_app", "source_url"]
        for field in required_fields:
            if field not in source_metadata:
                raise ValueError(f"Missing required metadata field: {field}")

        # Enforce user_id in metadata
        metadata = source_metadata.copy()
        metadata["user_id"] = user_id
        
        # Generate a unique ID (simple hash for now, or UUID)
        import hashlib
        doc_id = hashlib.md5((text + str(user_id) + metadata["source_url"]).encode()).hexdigest()

        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def query(self, user_id: int, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        # Enforce ACL by filtering on user_id
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where={"user_id": user_id}
        )
        return results

# Singleton instance
vector_db = ChromaDBClient()
