from app.services.vector_db import vector_db
from app.services.sanitizer import sanitizer
import shutil
import os
import chromadb

def test_sanitizer():
    print("Testing Sanitizer...")
    text = "Contact me at test@example.com or +1-555-555-0199."
    cleaned = sanitizer.mask_pii(text)
    print(f"Original: {text}")
    print(f"Cleaned:  {cleaned}")
    assert "[EMAIL]" in cleaned
    assert "[PHONE]" in cleaned
    print("Sanitizer Test Passed!")

def test_vector_db():
    print("\nTesting Vector DB...")
    
    # Add documents for User 1
    vector_db.index_document(
        user_id=1,
        text="This is a secret document for user 1.",
        source_metadata={"source_app": "notion", "source_url": "http://notion.so/doc1"}
    )
    vector_db.index_document(
        user_id=1,
        text="User 1 likes Python.",
        source_metadata={"source_app": "jira", "source_url": "http://jira.atlassian.com/issue/1"}
    )
    
    # Add documents for User 2
    vector_db.index_document(
        user_id=2,
        text="This is a secret document for user 2.",
        source_metadata={"source_app": "email", "source_url": "mailto:user2@example.com"}
    )
    vector_db.index_document(
        user_id=2,
        text="User 2 likes Java.",
        source_metadata={"source_app": "jira", "source_url": "http://jira.atlassian.com/issue/2"}
    )

    # Query for User 1
    print("Querying for User 1 (query='secret')...")
    results_u1 = vector_db.query(user_id=1, query_text="secret", n_results=2)
    print("Results:", results_u1['documents'][0])
    
    # Verify only User 1 docs returned
    for doc in results_u1['documents'][0]:
        assert "user 1" in doc.lower()
        assert "user 2" not in doc.lower()

    # Query for User 2
    print("Querying for User 2 (query='secret')...")
    results_u2 = vector_db.query(user_id=2, query_text="secret", n_results=2)
    print("Results:", results_u2['documents'][0])

    # Verify only User 2 docs returned
    for doc in results_u2['documents'][0]:
        assert "user 2" in doc.lower()
        assert "user 1" not in doc.lower()

    print("Vector DB ACL Test Passed!")

from app.core.config import settings

if __name__ == "__main__":
    # Use a test DB path to avoid locks
    TEST_DB_PATH = "./chroma_db_test"
    settings.CHROMA_DB_PATH = TEST_DB_PATH
    
    # Clean up previous DB if exists
    if os.path.exists(TEST_DB_PATH):
        shutil.rmtree(TEST_DB_PATH)
        
    try:
        # Re-initialize vector_db with new path
        vector_db.client = chromadb.PersistentClient(path=TEST_DB_PATH)
        vector_db.collection = vector_db.client.get_or_create_collection(name="personal_knowledge_base")
        
        test_sanitizer()
        test_vector_db()
    finally:
        # Cleanup
        # Note: Chroma client might hold lock, so cleanup might fail on Windows. 
        # We'll leave it or try best effort.
        pass
