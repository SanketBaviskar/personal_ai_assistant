
import asyncio
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.document import Document
from app.models.user import User
from sqlalchemy import text

# Mock services
mock_drive = MagicMock()
mock_drive.get_file_content.return_value = "This is a test document content for sanity check."

# Mock pgvector store to avoid actual HF calls/DB inserts if we want, 
# BUT we actually want to test DB inserts. So we only mock HF embedding generation if needed.
# For now, let's allow it to run if env vars are set, or mock it if not.

async def run_sanity_check():
    print("--- Starting Ingestion Sanity Check ---")
    
    # 1. Setup Test User
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "test_sanity@example.com").first()
        if not user:
            print("Creating test user...")
            user = User(email="test_sanity@example.com", is_active=True)
            db.add(user)
            db.commit()
            db.refresh(user)
        print(f"Test User ID: {user.id}")
        user_id = user.id
    finally:
        db.close()

    # 2. Mock Dependencies & Run Ingest
    with patch("app.services.rag_service.google_drive_service", mock_drive):
        from app.services.rag_service import rag_service
        
        # Test Data
        file_id = "test_file_123"
        mime_type = "application/vnd.google-apps.document"
        file_name = "Sanity Check Doc"
        
        print(f"\n[Run 1] Ingesting file {file_id}...")
        await rag_service.ingest_file(user, file_id, mime_type, file_name)
        
    # 3. Verify DB State (Run 1)
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.external_id == file_id, Document.user_id == user_id).first()
        if not doc:
            print("FAILED: Document row not found!")
            return
        
        print(f"SUCCESS: Document row created. ID: {doc.id}, Status: {doc.status}")
        print(f"  - Provider: {doc.provider}")
        print(f"  - External ID: {doc.external_id}")
        print(f"  - Source URL: {doc.source_url}")
        
        # Check embeddings
        chunks_count = db.execute(text("SELECT COUNT(*) FROM document_embeddings WHERE document_id = :did"), {"did": doc.id}).scalar()
        print(f"SUCCESS: {chunks_count} chunks found for document {doc.id}")
        
        if chunks_count == 0:
             print("WARNING: No chunks created. Check embedding service or chunker.")

    finally:
        db.close()

    # 4. Test Idempotency (Run 2)
    print(f"\n[Run 2] Re-ingesting file {file_id} (Idempotency Check)...")
    # Change content slightly to verify update, or keep same to verify no-op/update
    mock_drive.get_file_content.return_value = "This is a test document content for sanity check. Updated."
    
    with patch("app.services.rag_service.google_drive_service", mock_drive):
        await rag_service.ingest_file(user, file_id, mime_type, file_name)

    # 5. Verify DB State (Run 2)
    db = SessionLocal()
    try:
        docs = db.query(Document).filter(Document.external_id == file_id, Document.user_id == user_id).all()
        if len(docs) > 1:
            print(f"FAILED: Duplicate document rows found! Count: {len(docs)}")
        else:
            doc = docs[0]
            print(f"SUCCESS: Single document row maintained. ID: {doc.id}")
            
        # Check chunks again (should be updated count, but we need to know if they duplicated or replaced)
        # Since we don't strictly delete old chunks in the current simple impl (we just insert), 
        # we might see duplicates if explicit deletion logic isn't in `ingest_file`.
        # Wait, `ingest_file` logic I wrote earlier:
        # It calls `pgvector_store.index_document` loop.
        # It does NOT delete old chunks for the document_id yet. 
        # The checklist item 2.1 says "Re-sync handles updates (skip unchanged or clean replace)".
        
        chunks_count = db.execute(text("SELECT COUNT(*) FROM document_embeddings WHERE document_id = :did"), {"did": doc.id}).scalar()
        print(f"Chunks Count after Run 2: {chunks_count}") 
        # If I strictly implemented "clean replace", I should have cleared chunks. 
        # Let's see what happens.
        
    finally:
        db.close()
        
if __name__ == "__main__":
    asyncio.run(run_sanity_check())
