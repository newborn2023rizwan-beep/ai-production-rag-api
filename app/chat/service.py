from sqlalchemy.orm import Session

from app.database.models import ChatSession, Message, MessageSource, MessageRole
from app.rag.retrieval_pipeline import retrieve_context
from app.rag.prompt_builder import build_prompt
from app.llm.openai import generate_answer, generate_answer_stream


def create_session(db: Session) -> ChatSession:
    session = ChatSession()
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def send_message(db: Session, session_id, user_text: str, document_id=None) -> Message:
    user_message = Message(
        session_id=session_id,
        role=MessageRole.USER,
        message=user_text,
    )
    db.add(user_message)
    db.commit()

    result = retrieve_context(db, query=user_text, top_k=5, document_id=document_id)
    prompt = build_prompt(result)
    answer_text = generate_answer(prompt.system_prompt, prompt.user_prompt)

    assistant_message = Message(
        session_id=session_id,
        role=MessageRole.ASSISTANT,
        message=answer_text,
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    for chunk in result.chunks:
        source = MessageSource(
            message_id=assistant_message.id,
            chunk_id=chunk.id,
            similarity_score=chunk.similarity,
        )
        db.add(source)
    db.commit()

    return assistant_message


def send_message_stream(db: Session, session_id, user_text: str, document_id=None):
    user_message = Message(
        session_id=session_id,
        role=MessageRole.USER,
        message=user_text,
    )
    db.add(user_message)
    db.commit()

    result = retrieve_context(db, query=user_text, top_k=5, document_id=document_id)
    prompt = build_prompt(result)

    full_answer = ""
    for text_chunk in generate_answer_stream(prompt.system_prompt, prompt.user_prompt):
        full_answer += text_chunk
        yield text_chunk

    assistant_message = Message(
        session_id=session_id,
        role=MessageRole.ASSISTANT,
        message=full_answer,
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    for chunk in result.chunks:
        source = MessageSource(
            message_id=assistant_message.id,
            chunk_id=chunk.id,
            similarity_score=chunk.similarity,
        )
        db.add(source)
    db.commit()