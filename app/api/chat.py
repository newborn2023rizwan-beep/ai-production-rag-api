"""
Chat API.

Step 10 scope: expose the chat layer (Step 9) as real HTTP endpoints.
Step 11: streaming endpoint.
Step 14: source citations (page numbers) included in message responses.
Step 15: optional document_id to scope a chat to a single document.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db, SessionLocal
from app.database.models import ChatSession, Message, MessageRole, MessageSource, Chunk
from app.chat.service import create_session, send_message, send_message_stream

router = APIRouter(prefix="/chat", tags=["Chat"])


class SessionResponse(BaseModel):
    id: uuid.UUID
    created_at: str

    class Config:
        from_attributes = True


class MessageRequest(BaseModel):
    session_id: uuid.UUID
    message: str
    document_id: uuid.UUID | None = None


class SourceInfo(BaseModel):
    page_number: int | None
    similarity_score: float | None


class MessageResponse(BaseModel):
    id: uuid.UUID
    role: MessageRole
    message: str
    created_at: str
    sources: list[SourceInfo] = []

    class Config:
        from_attributes = True


def _session_to_response(session: ChatSession) -> SessionResponse:
    return SessionResponse(
        id=session.id,
        created_at=session.created_at.isoformat(),
    )


def _get_sources_for_message(db: Session, message_id) -> list[SourceInfo]:
    rows = (
        db.query(MessageSource, Chunk)
        .join(Chunk, MessageSource.chunk_id == Chunk.id)
        .filter(MessageSource.message_id == message_id)
        .order_by(MessageSource.similarity_score.desc())
        .all()
    )
    return [
        SourceInfo(page_number=chunk.page_number, similarity_score=source.similarity_score)
        for source, chunk in rows
    ]


def _message_to_response(db: Session, message: Message) -> MessageResponse:
    sources = _get_sources_for_message(db, message.id)
    return MessageResponse(
        id=message.id,
        role=message.role,
        message=message.message,
        created_at=message.created_at.isoformat(),
        sources=sources,
    )


@router.post("/session", response_model=SessionResponse)
def start_session(db: Session = Depends(get_db)):
    session = create_session(db)
    return _session_to_response(session)


@router.post("/message", response_model=MessageResponse)
def post_message(request: MessageRequest, db: Session = Depends(get_db)):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        answer = send_message(db, request.session_id, request.message, document_id=request.document_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {e}")

    return _message_to_response(db, answer)


@router.post("/message/stream")
def post_message_stream(request: MessageRequest):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    def event_generator():
        db = SessionLocal()
        try:
            for text_chunk in send_message_stream(db, request.session_id, request.message, document_id=request.document_id):
                yield text_chunk
        finally:
            db.close()

    return StreamingResponse(event_generator(), media_type="text/plain")