"""
PDF Upload API.

Step 2 scope: accept a PDF, validate it, save it to disk, and create a
`documents` row.
Step 13: automatically trigger the processing pipeline in the background.
Step 16: delete endpoint to remove a document and its chunks.
"""
import os
import uuid

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db, SessionLocal
from app.database.models import Document, DocumentStatus
from app.utils.validators import validate_pdf_upload
from app.utils.file_utils import build_safe_pdf_path, save_upload_to_disk
from app.document_processing.document_pipeline import create_document_record, process_document

router = APIRouter(prefix="/documents", tags=["Upload"])


class DocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    status: DocumentStatus
    uploaded_at: str

    class Config:
        from_attributes = True


def _to_response(doc: Document) -> DocumentResponse:
    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        status=doc.status,
        uploaded_at=doc.uploaded_at.isoformat(),
    )


def _run_pipeline_in_background(document_id):
    db = SessionLocal()
    try:
        process_document(db, document_id)
    finally:
        db.close()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()
    validate_pdf_upload(file, file_size=len(file_bytes))

    stored_filename, full_path = build_safe_pdf_path(file.filename)

    try:
        save_upload_to_disk(file_bytes, full_path)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    document = create_document_record(
        db=db,
        filename=file.filename,
        file_path=str(full_path),
    )

    background_tasks.add_task(_run_pipeline_in_background, document.id)

    return _to_response(document)


@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).order_by(Document.uploaded_at.desc()).all()
    return [_to_response(d) for d in documents]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: uuid.UUID, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    return _to_response(document)


@router.delete("/{document_id}")
def delete_document(document_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Deletes a document and its chunks (cascade). Uses a raw SQL delete
    so Postgres handles the cascade directly (documents -> chunks ->
    message_sources), instead of SQLAlchemy's ORM trying to manually
    null out foreign keys that aren't nullable.
    """
    from sqlalchemy import text

    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    file_path = document.file_path

    db.execute(text("DELETE FROM documents WHERE id = :id"), {"id": str(document_id)})
    db.commit()

    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass

    return {"deleted": True, "id": str(document_id)}