
import sys
import os
from sqlalchemy import text

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine

def apply_migration():
    print("Applying migration 006 (Move vector extension)...")
    migration_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "migrations", "006_move_vector_extension.sql")
    
    with open(migration_file, "r") as f:
        sql = f.read()

    # Split by semicolon if needed, but for simple statements execute might handle it or need split.
    # ALTER commands often need individual execution in some drivers, 
    # but SQLAlchemy execute(text()) with multiline string usually works for Postgres if driver supports it.
    # However, let's split safely.
    statements = [s.strip() for s in sql.split(';') if s.strip()]

    # Split logic
    raw_statements = sql.split(';')
    statements = []
    for s in raw_statements:
        s = s.strip()
        if s and not s.startswith('--'):
             statements.append(s)

    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        for stmt in statements:
            if not stmt: continue
            try:
                print(f"Executing: {stmt[:50]}...")
                conn.execute(text(stmt))
                # Auto-commit enables, no need for conn.commit()
            except Exception as e:
                print(f"Error executing statement: {e}")
                # Don't raise immediately, try next? No, fail fast is better.
                # But ALTER DATABASE might fail if not owner.
                if "must be owner of database" in str(e):
                    print("SKIPPING: Not owner of database.")
                    continue
                if "role" in str(e) and "does not exist" in str(e):
                     print("SKIPPING: Role does not exist.")
                     continue
                raise

    print("Migration 006 applied successfully.")

if __name__ == "__main__":
    apply_migration()
