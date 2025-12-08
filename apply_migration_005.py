import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sqlalchemy import create_engine, text
from app.core.config import settings

def apply():
    db_url = settings.sync_database_url
    if not db_url:
        print("DATABASE_URL is not set.")
        return
        
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    engine = create_engine(db_url)
    
    file_path = os.path.join(os.path.dirname(__file__), "migrations/005_align_schema_and_rls.sql")
    with open(file_path, "r") as f:
        sql = f.read()
    
    print(f"Applying migration from {file_path}...")
    try:
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
        print("Migration applied successfully.")
    except Exception as e:
        print(f"Error applying migration: {e}")

if __name__ == "__main__":
    apply()
