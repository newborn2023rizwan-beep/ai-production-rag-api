"""
Generate Embeddings.

Uses a local sentence-transformers model — runs entirely inside this
container, no external API calls, no document text ever leaves the
server. Important for confidential documents (legal, medical, etc.).

The model is downloaded once (on first use) and cached inside the
container at ~/.cache/torch/sentence_transformers/. On a fresh container
build this means the first embedding call will take longer (downloading
~80MB); subsequent calls are fast.
"""
from sentence_transformers import SentenceTransformer

from app.config.settings import settings

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """
    Lazily loads the embedding model once per process and reuses it.
    Loading is deferred (not done at import time) so that importing this
    module doesn't trigger a slow model download — it only happens when
    embeddings are actually needed.
    """
    global _model
    if _model is None:
        # settings.EMBEDDING_MODEL looks like "sentence-transformers/all-MiniLM-L6-v2";
        # SentenceTransformer accepts that full path directly.
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embeds a batch of texts, returning one vector per input text (same order).
    Vector length matches settings.EMBEDDING_DIM (384 for all-MiniLM-L6-v2).
    """
    if not texts:
        return []
    model = _get_model()
    vectors = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    """Convenience wrapper for embedding a single query string (used in Step 6)."""
    return embed_texts([text])[0]
