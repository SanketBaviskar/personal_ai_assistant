import os
import sys

# Add the parent directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from app.db.base import Base
from app.core.config import settings

def init_db():
    # settings.sync_database_url will automatically load from .env if DATABASE_URL is set there
    database_url = settings.sync_database_url
    
    # Check if we are still using the default SQLite
    if "sqlite" in database_url and not os.getenv("DATABASE_URL"):
        print("Warning: Using default SQLite database.")
        print("If you intended to use Supabase, ensure DATABASE_URL is set in your .env file.")
        # We continue anyway, as it might be intentional for testing
    
    if not database_url:
        print("Error: Could not determine database URL.")
        return

    print(f"Connecting to database...")
    # Handle postgres:// vs postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    try:
        engine = create_engine(database_url)
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    init_db()
