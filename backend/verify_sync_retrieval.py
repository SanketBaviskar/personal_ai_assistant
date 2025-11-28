from app.services.processing.sync_service import sync_service
from app.services.ai_core.retriever import retriever
from app.services.vector_db import vector_db
from app.core.config import settings
import shutil
import os
import chromadb

def test_sync_and_retrieval():
    print("Testing Sync and Retrieval...")
    
    user_id = 101
    
    # 0. Store Credentials (Mock)
    from app.services.credential_service import credential_service
    from app.db.session import SessionLocal
    
    db = SessionLocal()
    credential_service.store_credentials(db, user_id, "notion", {"api_key": "mock_key"})
    db.close()

    # 1. Run Sync (Mocked Connectors will return data)
    print("Running Sync...")
    sync_service.sync_user_data(user_id)
    
    # 2. Run Retrieval
    print("Running Retrieval...")
    query = "project plan"
    results = retriever.retrieve_context(user_id, query)
    
    print(f"Retrieved {len(results)} documents.")
    for doc in results:
        print(f"Text: {doc['text'][:50]}...")
        print(f"Metadata: {doc['source_metadata']}")
        assert doc['source_metadata']['user_id'] == user_id
        
    assert len(results) > 0
    print("Sync and Retrieval Test Passed!")

if __name__ == "__main__":
    # Use a test DB path
    TEST_DB_PATH = "./chroma_db_sync_test"
    settings.CHROMA_DB_PATH = TEST_DB_PATH
    
    if os.path.exists(TEST_DB_PATH):
        shutil.rmtree(TEST_DB_PATH)
        
    try:
        # Re-init DB with test path
        vector_db.client = chromadb.PersistentClient(path=TEST_DB_PATH)
        vector_db.collection = vector_db.client.get_or_create_collection(name="personal_knowledge_base")
        
        test_sync_and_retrieval()
    finally:
        pass
