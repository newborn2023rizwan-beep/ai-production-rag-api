"""
Vector Similarity Search.

Finds the most relevant chunks from the vector database using
cosine distance (via pgvector's <=> operator).

Step 15: added optional document_id filter, so retrieval can be scoped
to a single document instead of searching across all uploaded documents.
"""
from sqlalchemy import text
from sqlalchemy.orm import Session
import json

from app.database.models import Chunk
from app.document_processing.embedding_service import embed_query


class ChunkSearchResult:
    """Wrapper for chunk search results with similarity scores."""

    def __init__(self, chunk: Chunk, similarity: float):
        self.id = chunk.id
        self.document_id = chunk.document_id
        self.chunk_index = chunk.chunk_index
        self.page_number = chunk.page_number
        self.chunk_text = chunk.chunk_text
        self.embedding_vector = chunk.embedding_vector
        self.embedding_model = chunk.embedding_model
        self.similarity = similarity


def search_chunks(
    db: Session,
    query: str,
    top_k: int = 5,
    document_id=None,
) -> list[ChunkSearchResult]:
    """
    Search for the most relevant chunks using vector similarity (cosine distance).
    If document_id is provided, only chunks from that document are searched.
    """
    query_vector = embed_query(query)
    vector_str = json.dumps(query_vector)

    document_filter = ""
    params = {}
    if document_id is not None:
        document_filter = "AND document_id = :document_id"
        params["document_id"] = str(document_id)

    query_sql = f"""
        SELECT
            id,
            document_id,
            chunk_index,
            page_number,
            chunk_text,
            embedding_vector,
            embedding_model,
            1 - (embedding_vector <=> '{vector_str}'::vector) as similarity
        FROM chunks
        WHERE embedding_vector IS NOT NULL
        {document_filter}
        ORDER BY similarity DESC
        LIMIT {top_k}
    """

    raw_results = db.execute(text(query_sql), params)

    results = []
    for row in raw_results:
        chunk = Chunk(
            id=row.id,
            document_id=row.document_id,
            chunk_index=row.chunk_index,
            page_number=row.page_number,
            chunk_text=row.chunk_text,
            embedding_vector=row.embedding_vector,
            embedding_model=row.embedding_model,
        )
        results.append(ChunkSearchResult(chunk, similarity=row.similarity))

    return results