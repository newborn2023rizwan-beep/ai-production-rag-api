from typing import List
from dataclasses import dataclass

from app.rag.retrieval_pipeline import RetrievalResult


DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant that answers questions strictly using the provided document context.

Rules:
- Only use information found in the "Context" section below to answer.
- If the context does not contain enough information to answer the question, say so clearly instead of guessing.
- When you use information from a specific part of the context, cite its page number in parentheses, e.g. "(Page 12)".
- Do not fabricate page numbers or content that is not present in the context.
- Keep answers clear and directly relevant to the question asked."""


@dataclass
class BuiltPrompt:
    system_prompt: str
    user_prompt: str
    source_chunk_ids: List[str]


def build_prompt(
    retrieval_result: RetrievalResult,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
) -> BuiltPrompt:
    if not retrieval_result.has_context:
        user_prompt = (
            f"Context: (no relevant document content was found)\n\n"
            f"Question: {retrieval_result.query}"
        )
        return BuiltPrompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            source_chunk_ids=[],
        )

    context_blocks = []
    source_chunk_ids = []

    for chunk in retrieval_result.chunks:
        page_label = f"Page {chunk.page_number}" if chunk.page_number is not None else "Page unknown"
        context_blocks.append(f"[{page_label}]\n{chunk.chunk_text}")
        source_chunk_ids.append(str(chunk.id))

    context_text = "\n\n---\n\n".join(context_blocks)

    user_prompt = (
        f"Context:\n{context_text}\n\n"
        f"Question: {retrieval_result.query}"
    )

    return BuiltPrompt(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        source_chunk_ids=source_chunk_ids,
    )