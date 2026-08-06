"""
Database-specific configuration constants.
Kept separate from settings.py so DB tuning (pool size, echo, etc.)
can evolve independently of general app settings.
"""
from app.config.settings import settings

DATABASE_URL: str = settings.DATABASE_URL

# SQLAlchemy engine tuning (safe MVP defaults)
DB_POOL_SIZE = 5
DB_MAX_OVERFLOW = 10
DB_ECHO_SQL = settings.APP_ENV.lower() == "development"
