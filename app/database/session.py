"""
Database engine + session management.
Provides a FastAPI-compatible dependency (get_db) for use in API routes
starting from Step 2 onward.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config.database import DATABASE_URL, DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_ECHO_SQL

engine = create_engine(
    DATABASE_URL,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    echo=DB_ECHO_SQL,
    pool_pre_ping=True,  # avoids stale connection errors after idle periods
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency: yields a DB session and guarantees it's closed."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
