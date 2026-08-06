"""
Runs the Step 3+4 pipeline (extract -> clean -> chunk) on a document and
prints a detailed preview so you can visually confirm the results are good
before moving on to embeddings (Step 5).

Usage:
    docker-compose exec backend python scripts/process_document.py
        -> processes the most recently uploaded document

    docker-compose exec backend python scripts/process_document.py <document_id>
        -> processes a specific document by its UUID (from GET /documents)
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.session import SessionLocal
from app.database.models import Document, Chunk, DocumentStatus
from app.document_processing.document_pipeline import process_document


def print_separator():
    print("-" * 70)


def main():
    db = SessionLocal()
    try:
        if len(sys.argv) > 1:
            document_id = sys.argv[1]
            document = db.query(Document).filter(Document.id == document_id).first()
            if document is None:
                print(f"No document found with id {document_id}")
                return
        else:
            document = db.query(Document).order_by(Document.uploaded_at.desc()).first()
            if document is None:
                print("No documents found. Upload one first via POST /documents/upload.")
                return

        print(f"Processing document: {document.filename} (id={document.id})")
        print_separator()

        result = process_document(db, document.id)

        if result.status == DocumentStatus.FAILED:
            print(f"FAILED: {result.error_message}")
            return

        chunks = (
            db.query(Chunk)
            .filter(Chunk.document_id == result.id)
            .order_by(Chunk.chunk_index)
            .all()
        )

        chunk_lengths = [len(c.chunk_text) for c in chunks]
        print(f"Status: {result.status.value}")
        print(f"Total chunks created: {len(chunks)}")
        if chunk_lengths:
            print(f"Chunk length — min: {min(chunk_lengths)}, "
                  f"max: {max(chunk_lengths)}, "
                  f"avg: {sum(chunk_lengths) // len(chunk_lengths)}")
        print_separator()

        preview_count = min(3, len(chunks))
        print(f"Previewing first {preview_count} chunks:\n")
        for c in chunks[:preview_count]:
            print(f"[chunk {c.chunk_index} | page {c.page_number} | {len(c.chunk_text)} chars]")
            print(c.chunk_text[:400])
            print_separator()

        if len(chunks) > preview_count:
            last = chunks[-1]
            print(f"Last chunk [chunk {last.chunk_index} | page {last.page_number} | "
                  f"{len(last.chunk_text)} chars]:")
            print(last.chunk_text[:400])
            print_separator()

    finally:
        db.close()


if __name__ == "__main__":
    main()
