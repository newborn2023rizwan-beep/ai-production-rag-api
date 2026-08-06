from typing import List, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session

from app.rag.vector_search import search_chunks, ChunkSearchResult


@dataclass
class RetrievalResult:
    query: str
    chunks: List[ChunkSearchResult]
    has_context: bool


def retrieve_context(
    db: Session,
    query: str,
    top_k: int = 5,
    document_id: Optional[str] = None,
) -> RetrievalResult:
    if not query or not query.strip():
        raise ValueError("Query text cannot be empty.")

    results = search_chunks(db, query=query, top_k=top_k, document_id=document_id)

    return RetrievalResult(
        query=query,
        chunks=results,
        has_context=len(results) > 0,
    )