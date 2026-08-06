"""
Loads environment variables from .env file into process environment.
Must be imported before any other config module reads os.environ.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Project root is two levels up from this file: app/config/env.py -> backend/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)
else:
    # In Docker, env vars are usually injected directly via docker-compose
    # so a missing .env file here is not necessarily an error.
    pass


def get_env(key: str, default: str = None) -> str:
    """Small helper to fetch an environment variable with an optional default."""
    return os.getenv(key, default)
