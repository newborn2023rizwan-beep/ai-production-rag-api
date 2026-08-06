"""
Complete Document Processing Pipeline.

Steps implemented so far:
    Step 2: create_document_record()  -> save upload metadata, status=PROCESSING
    Step 3: pdf_loader + text_cleaner -> extract + clean raw text
    Step 4: chunker                   -> split into chunks, store in DB
    Step 5: embedding_service + vector_repository -> embed each chunk,
            flip status to READY (document is now queryable)

Still pending:
    Step 6: rag/vector_search.py -> actually search these embeddings
            given a question (this is what makes the document useful).
"""
from sqlalchemy.orm import Session

from app.database.models import Document, DocumentStatus, Chunk
from app.document_processing.loaders.pdf_loader import load_pdf, PdfLoadError
from app.document_processing.text_cleaner import clean_pages
from app.document_processing.chunker import chunk_pages
from app.document_processing.embedding_service import embed_texts
from app.document_processing.vector_repository import store_embeddings_for_chunks


def create_document_record(
    db: Session,
    filename: str,
    file_path: str,
) -> Document:
    """
    Creates the initial `documents` row right after a file is saved to disk.
    Status starts as PROCESSING — process_document() below does the actual work.
    """
    document = Document(
        filename=filename,
        file_path=file_path,
        status=DocumentStatus.PROCESSING,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def process_document(db: Session, document_id) -> Document:
    """
    Runs the full pipeline for a document: extract -> clean -> chunk -> embed.
    On success, status becomes READY (the document is now queryable via Step 6+).
    On any failure, status becomes FAILED with error_message set, rather than
    raising — so callers (a script, or a future background worker) can just
    check document.status afterward.

    Safe to re-run: existing chunks for this document are deleted first,
    so reprocessing doesn't create duplicates or stale embeddings.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if document is None:
        raise ValueError(f"No document found with id {document_id}")

    try:
        pages = load_pdf(document.file_path)
        cleaned = clean_pages(pages)
        chunk_data_list = chunk_pages(cleaned)

        if not chunk_data_list:
            raise PdfLoadError(
                "No extractable text found in this PDF (it may be scanned "
                "images without OCR, which isn't supported yet)."
            )

        # Idempotent re-processing: wipe old chunks for this document first.
        db.query(Chunk).filter(Chunk.document_id == document.id).delete()
        db.flush()

        new_chunks = [
            Chunk(
                document_id=document.id,
                chunk_index=chunk_data.chunk_index,
                page_number=chunk_data.page_number,
                chunk_text=chunk_data.chunk_text,
                embedding_vector=None,
                embedding_model=None,
            )
            for chunk_data in chunk_data_list
        ]
        db.add_all(new_chunks)
        db.flush()  # assigns IDs without committing yet

        # Step 5: embed every chunk's text and store the vectors.
        texts = [c.chunk_text for c in new_chunks]
        vectors = embed_texts(texts)
        store_embeddings_for_chunks(db, new_chunks, vectors)

        document.status = DocumentStatus.READY
        document.error_message = None
        db.commit()
        db.refresh(document)
        return document

    except Exception as e:
        db.rollback()
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)
        db.commit()
        db.refresh(document)
        return document
