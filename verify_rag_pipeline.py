from app.services.processing.rag_pipeline import rag_pipeline
from app.services.vector_db import vector_db
import shutil
import os
import chromadb
from app.core.config import settings

def test_rag_pipeline():
    print("Testing RAG Pipeline...")
    
    # Sample long document
    long_text = """
    This is a long document about Artificial Intelligence.
    AI is transforming the world.
    
    Section 1: Machine Learning.
    Machine learning is a subset of AI. It involves training models on data.
    Deep learning is a subset of machine learning.
    
    Section 2: Natural Language Processing.
    NLP focuses on the interaction between computers and human language.
    Large Language Models (LLMs) are a key part of modern NLP.
    """
    
    user_id = 99
    source_metadata = {
        "source_app": "notion",
        "source_url": "https://notion.so/ai-doc"
    }

    # Process document
    print("Processing document...")
    chunks_count = rag_pipeline.process_document(user_id, long_text, source_metadata)
    print(f"Processed {chunks_count} chunks.")
    
    assert chunks_count > 0

    # Verify in DB
    print("Verifying in Vector DB...")
    results = vector_db.query(user_id=user_id, query_text="machine learning", n_results=5)
    
    docs = results['documents'][0]
    metadatas = results['metadatas'][0]
    
    print(f"Found {len(docs)} relevant chunks.")
    for i, doc in enumerate(docs):
        print(f"Chunk {i}: {doc[:50]}...")
        print(f"Metadata: {metadatas[i]}")
        assert metadatas[i]['user_id'] == user_id
        assert metadatas[i]['source_app'] == "notion"
        assert "chunk_index" in metadatas[i]

    print("RAG Pipeline Test Passed!")

if __name__ == "__main__":
    # Use a test DB path
    TEST_DB_PATH = "./chroma_db_rag_test"
    settings.CHROMA_DB_PATH = TEST_DB_PATH
    
    if os.path.exists(TEST_DB_PATH):
        shutil.rmtree(TEST_DB_PATH)
        
    try:
        # Re-init DB with test path
        vector_db.client = chromadb.PersistentClient(path=TEST_DB_PATH)
        vector_db.collection = vector_db.client.get_or_create_collection(name="personal_knowledge_base")
        
        test_rag_pipeline()
    finally:
        pass
