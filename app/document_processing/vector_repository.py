"""
PGVector Operations.

Handles writing embedding vectors onto existing `chunks` rows.
(Reading/searching vectors is Step 6 — rag/vector_search.py.)
"""
from sqlalchemy.orm import Session

from app.database.models import Chunk
from app.config.settings import settings


def store_embeddings_for_chunks(
    db: Session,
    chunks: list[Chunk],
    vectors: list[list[float]],
) -> None:
    """
    Assigns each chunk its corresponding embedding vector and commits.
    `chunks` and `vectors` must be the same length and in matching order.
    """
    if len(chunks) != len(vectors):
        raise ValueError(
            f"Mismatch between chunk count ({len(chunks)}) and vector count ({len(vectors)})"
        )

    for chunk, vector in zip(chunks, vectors):
        chunk.embedding_vector = vector
        chunk.embedding_model = settings.EMBEDDING_MODEL

    db.commit()
