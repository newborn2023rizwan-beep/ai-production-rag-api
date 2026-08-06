"""
Initializes the database for this project:
1. Enables the pgvector extension (required for the chunks.embedding_vector column).
2. Creates all tables defined in app/database/models.py.

Run this once after the containers are up:
    docker-compose exec backend python scripts/create_db.py

Safe to re-run: CREATE EXTENSION IF NOT EXISTS and create_all() are both idempotent.
"""
import sys
import os

# Allow running this script directly (adds project root to path)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.database.session import engine
from app.database.base import Base
from app.database import models  # noqa: F401  (ensures models are registered on Base)


def main():
    print("Connecting to database...")
    with engine.connect() as conn:
        print("Enabling pgvector extension (if not already enabled)...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    print("Creating tables from models (if not already created)...")
    Base.metadata.create_all(bind=engine)

    print("Done. Tables created:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")


if __name__ == "__main__":
    main()
