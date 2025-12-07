from app.db.session import engine
from sqlalchemy import text

def run_migration():
    with open("migrations/004_add_conversation_id_to_documents.sql", "r") as f:
        sql = f.read()
    
    with engine.connect() as conn:
        for statement in sql.split(";"):
            if statement.strip():
                try:
                    conn.execute(text(statement))
                    conn.commit()
                    print(f"Executed: {statement[:50]}...")
                except Exception as e:
                    print(f"Skipping error (maybe already exists): {e}")

if __name__ == "__main__":
    run_migration()
