"""
LLM provider configuration.
Step 8 — LLM integration.
"""
from app.config.settings import settings

LLM_PROVIDER = settings.LLM_PROVIDER
OPENAI_API_KEY = settings.OPENAI_API_KEY
OPENAI_MODEL = "gpt-4o-mini"

DEFAULT_MAX_TOKENS = 1024
DEFAULT_TEMPERATURE = 0.2