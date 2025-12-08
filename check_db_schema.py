import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sqlalchemy import create_engine, inspect
from app.core.config import settings

def check():
    db_url = settings.sync_database_url
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    engine = create_engine(db_url)
    insp = inspect(engine)
    
    print("Checking 'document' columns:")
    cols = [c['name'] for c in insp.get_columns("document")]
    print(cols)
    
    required_doc = ["provider", "external_id", "source_url", "content_hash"]
    missing_doc = [c for c in required_doc if c not in cols]
    
    print("Checking 'document_embeddings' columns:")
    emb_cols = [c['name'] for c in insp.get_columns("document_embeddings")]
    print(emb_cols)
    
    required_emb = ["document_id"]
    missing_emb = [c for c in required_emb if c not in emb_cols]

    print("Checking 'messages' columns:")
    msg_cols = [c['name'] for c in insp.get_columns("messages")]
    print(msg_cols)
    
    required_msg = ["user_id"]
    missing_msg = [c for c in required_msg if c not in msg_cols]
    
    if not missing_doc and not missing_emb and not missing_msg:
        print("SUCCESS: All columns present.")
    else:
        print(f"FAILED: Missing columns: Document={missing_doc}, Embeddings={missing_emb}, Messages={missing_msg}")

if __name__ == "__main__":
    check()
