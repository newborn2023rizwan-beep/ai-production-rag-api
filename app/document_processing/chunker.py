"""
Chunk Generator.

Splits cleaned page text into overlapping chunks suitable for embedding.
Chunking happens per-page (not across the whole document) so each chunk
keeps an accurate page_number — useful later for citations ("source:
page 4").

Chunks target CHUNK_SIZE characters, but the boundary is nudged to the
nearest sentence end where possible, so we don't cut off mid-sentence
and hurt embedding/retrieval quality.
"""
import re
from dataclasses import dataclass

from app.document_processing.loaders.pdf_loader import PageContent
from app.config.rag import CHUNK_SIZE, CHUNK_OVERLAP

# How far past the target chunk_size we're willing to look for a clean
# sentence-ending boundary before just cutting at chunk_size anyway.
SENTENCE_BOUNDARY_LOOKAHEAD = 100


@dataclass
class ChunkData:
    chunk_index: int      # 0-indexed position among all chunks for this document
    page_number: int
    chunk_text: str


def _find_sentence_boundary(text: str, target_end: int) -> int:
    """
    Looks for a sentence-ending punctuation mark shortly after target_end,
    so chunks end on natural boundaries instead of mid-word/mid-sentence.
    Falls back to target_end if none is found nearby.
    """
    lookahead_window = text[target_end:target_end + SENTENCE_BOUNDARY_LOOKAHEAD]
    match = re.search(r"[.!?]\s", lookahead_window)
    if match:
        return target_end + match.end()
    return target_end


def chunk_pages(
    pages: list[PageContent],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[ChunkData]:
    """
    Splits each page's text into overlapping chunks.
    Empty pages (e.g. a page that was all image, no extractable text)
    are skipped entirely.
    """
    chunks: list[ChunkData] = []
    global_index = 0

    for page in pages:
        text = page.raw_text.strip()
        if not text:
            continue

        length = len(text)
        start = 0

        while start < length:
            target_end = min(start + chunk_size, length)
            end = target_end if target_end >= length else _find_sentence_boundary(text, target_end)
            end = min(end, length)

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    ChunkData(
                        chunk_index=global_index,
                        page_number=page.page_number,
                        chunk_text=chunk_text,
                    )
                )
                global_index += 1

            if end >= length:
                break

            # Move start forward, backing up by `overlap` so consecutive
            # chunks share context (helps retrieval near chunk boundaries).
            next_start = end - overlap
            start = next_start if next_start > start else end

    return chunks
