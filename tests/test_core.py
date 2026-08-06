"""
Basic smoke tests for the RAG backend.

Not exhaustive coverage — just enough to catch obvious breakage in the
core flows: upload validation, document processing, and chat.
Run with: pytest tests/test_core.py -v
"""
import io
import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.session import SessionLocal
from app.database.models import Document, ChatSession, Message

client = TestClient(app)


def test_health_check():
    """Basic sanity check that the app boots and responds."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_upload_rejects_non_pdf():
    """Uploading a non-PDF file should be rejected, not silently accepted."""
    fake_file = io.BytesIO(b"this is not a pdf")
    response = client.post(
        "/documents/upload",
        files={"file": ("test.txt", fake_file, "text/plain")},
    )
    assert response.status_code in (400, 422)


def test_upload_accepts_valid_pdf_and_cleans_up():
    """
    Uploading a minimal valid PDF should succeed and create a document
    row. Cleans up after itself so tests don't pollute the real database.
    """
    minimal_pdf = (
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]>>endobj\n"
        b"xref\n0 4\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n0\n%%EOF"
    )
    fake_file = io.BytesIO(minimal_pdf)

    response = client.post(
        "/documents/upload",
        files={"file": ("smoke_test.pdf", fake_file, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "smoke_test.pdf"
    assert data["status"] in ("uploading", "processing", "ready", "failed")

    doc_id = data["id"]

    db = SessionLocal()
    try:
        db.query(Document).filter(Document.id == uuid.UUID(doc_id)).delete()
        db.commit()
    finally:
        db.close()


def test_create_chat_session():
    """Creating a chat session should return a valid session id."""
    response = client.post("/chat/session")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "created_at" in data

    db = SessionLocal()
    try:
        db.query(ChatSession).filter(ChatSession.id == uuid.UUID(data["id"])).delete()
        db.commit()
    finally:
        db.close()


def test_chat_message_rejects_empty_message():
    """An empty message should be rejected before hitting the LLM."""
    session_response = client.post("/chat/session")
    session_id = session_response.json()["id"]

    response = client.post(
        "/chat/message",
        json={"session_id": session_id, "message": "   "},
    )
    assert response.status_code == 400

    db = SessionLocal()
    try:
        db.query(ChatSession).filter(ChatSession.id == uuid.UUID(session_id)).delete()
        db.commit()
    finally:
        db.close()