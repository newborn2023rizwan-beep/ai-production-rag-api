"""
FastAPI Entry Point.

Step 1: health check router (backend <-> Postgres connectivity).
Step 2: upload router (PDF upload + document status).
Step 10: chat router (chat sessions + messages).
Step 12: CORS enabled for frontend (React dev server on localhost:5173).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, upload, chat

app = FastAPI(
    title="RAG Document Assistant API",
    description="Backend for PDF-based Retrieval-Augmented Generation chat.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://ai-knowledge-base-chatbot.local"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(upload.router)
app.include_router(chat.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "RAG Document Assistant API is running.",
        "docs": "/docs",
    }