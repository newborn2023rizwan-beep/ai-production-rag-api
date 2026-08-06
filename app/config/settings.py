"""
Global application settings.
Reads from environment variables (populated via .env in local/dev,
or via docker-compose / VPS environment injection in production).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config import env  # noqa: F401  (ensures .env is loaded first)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Database
    DATABASE_URL: str

    # Embeddings (used starting Step 5, present now for completeness)
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    # LLM (used starting Step 7)
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"


# Singleton instance imported throughout the app
settings = Settings()
