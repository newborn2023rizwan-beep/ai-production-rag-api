# ai-production-rag-api


A production-oriented **Retrieval Augmented Generation (RAG) backend** built with FastAPI, OpenAI models, document processing, embeddings, vector search, and structured retrieval pipelines.

This system provides the **intelligence layer** for AI knowledge assistants that need to answer questions using private documents, business knowledge, and domain-specific information rather than relying only on an LLM's pretrained knowledge.

---

# 1. Introduction

Traditional AI applications generate responses primarily from the knowledge already available inside the language model.

The **ai-production-rag-api** adds an external knowledge retrieval layer between the user and the AI model.

Instead of sending a question directly to an LLM, the system first searches the application's knowledge base, retrieves the most relevant information, builds contextual prompts, and then sends that context to the LLM for response generation.

```text
User Question
      ↓
Knowledge Retrieval
      ↓
Relevant Context
      ↓
Prompt Construction
      ↓
LLM Generation
      ↓
Final Answer
```

This architecture helps build AI assistants that can work with **private, domain-specific, and frequently changing information**.

---

# 2. Overview

The backend is designed as a reusable **Production RAG API** that can serve different client applications.

For example:

```text
                    Production RAG API
                           │
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
        WordPress       Web App       Custom App
        AI Assistant    AI Assistant    / API Client
```

The client application does not need to implement the complete RAG pipeline itself.

The backend handles:

* Document ingestion
* Text extraction
* Text cleaning
* Chunking
* Embedding generation
* Vector storage
* Semantic retrieval
* Context construction
* LLM communication
* AI response generation

---

# 3. Business Purpose

The primary purpose of this system is to provide businesses with a reusable AI knowledge infrastructure that can turn their private documents and business information into an intelligent, queryable knowledge base. Instead of building a separate RAG system for every application, the **Production RAG API** can serve multiple client applications such as WordPress assistants, web applications, internal knowledge assistants, customer-support systems, and other AI products. This creates a scalable foundation for building and deploying business-specific AI assistants while keeping the retrieval and AI intelligence centralized in a dedicated backend.

---

# 4. Core Features

## Document Processing

* PDF document processing
* Text extraction
* Text cleaning
* Document chunking
* Embedding generation
* Vector storage
* Document processing pipeline

## RAG & Retrieval

* Semantic vector search
* Relevant context retrieval
* Retrieval pipeline
* Context-aware prompt construction
* Knowledge-grounded response generation

## AI Generation

* OpenAI API integration
* LLM-based response generation
* Centralized prompt management
* Context-aware AI responses

## API

* FastAPI REST API
* Chat endpoint
* Document upload endpoint
* Health check endpoint

## Infrastructure

* Docker support
* Docker Compose
* Environment-based configuration
* Database session management
* Production-oriented project structure

---

# 5. System Architecture

```text
                         Client Application
                                │
                                ↓
                     ┌────────────────────┐
                     │    FastAPI API     │
                     │                    │
                     │  Chat / Upload /   │
                     │      Health        │
                     └─────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ↓                ↓                ↓
        Chat Service    Document Pipeline    Config
              │                │
              │                ↓
              │        ┌───────────────┐
              │        │ PDF Loader    │
              │        │ Text Cleaner  │
              │        │ Chunker       │
              │        │ Embeddings    │
              │        └───────┬───────┘
              │                │
              │                ↓
              │        Vector Repository
              │                │
              └────────┬───────┘
                       ↓
                Retrieval Pipeline
                       │
                       ↓
                 Vector Search
                       │
                       ↓
                Prompt Builder
                       │
                       ↓
                  OpenAI LLM
                       │
                       ↓
                 Final Response
```

---

# 6. How the System Works

The system has two primary workflows: **document ingestion** and **question answering**.

## Document Ingestion Workflow

```text
Document Upload
      ↓
Document Loader
      ↓
Text Extraction
      ↓
Text Cleaning
      ↓
Chunking
      ↓
Embedding Generation
      ↓
Vector Storage
      ↓
Knowledge Base Ready
```

The document is transformed into smaller searchable chunks and converted into vector representations before being stored for retrieval.

---

## Question Answering Workflow

```text
User Question
      ↓
Chat API
      ↓
Query Processing
      ↓
Vector Search
      ↓
Relevant Chunks
      ↓
Context Building
      ↓
Prompt Builder
      ↓
OpenAI
      ↓
AI Response
      ↓
Client Application
```

The LLM receives relevant retrieved context rather than relying only on its pretrained knowledge.

---

# 7. Technology Stack

## Backend

* Python
* FastAPI
* Uvicorn

## AI / LLM

* OpenAI API
* Large Language Models
* Embedding Models
* Retrieval Augmented Generation

## Document Processing

* PDF document loaders
* Text cleaning
* Chunking pipeline
* Embedding service

## Data & Retrieval

* SQL database
* Vector storage
* Vector similarity search
* Retrieval pipeline

## Infrastructure

* Docker
* Docker Compose
* Environment-based configuration

---

# 8. Project Structure

```text
production-rag-api/
│
├── app/
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── health.py
│   │   └── upload.py
│   │
│   ├── chat/
│   │   └── service.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── env.py
│   │   ├── llm.py
│   │   ├── prompts.py
│   │   ├── rag.py
│   │   └── settings.py
│   │
│   ├── database/
│   │   ├── migrations/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── models.py
│   │   └── session.py
│   │
│   ├── document_processing/
│   │   ├── loaders/
│   │   │   ├── __init__.py
│   │   │   └── pdf_loader.py
│   │   │
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── document_pipeline.py
│   │   ├── embedding_service.py
│   │   ├── text_cleaner.py
│   │   └── vector_repository.py
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   └── openai.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── prompt_builder.py
│   │   ├── retrieval_pipeline.py
│   │   └── vector_search.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_utils.py
│   │   └── validators.py
│   │
│   ├── __init__.py
│   └── main.py
│
├── logs/
│   └── .gitkeep
│
├── scripts/
│   ├── backup_db.py
│   ├── create_db.py
│   ├── process_document.py
│   ├── rebuild_vectors.py
│   └── seed_data.py
│
├── tests/
│   └── test_core.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
├── SPECIFICATION.md
├── docker-compose.yml
└── requirements.txt
```

---

# 9. Architecture Components

## API Layer

The API layer exposes the backend functionality to client applications.

Main responsibilities:

* Receive client requests
* Validate input
* Trigger backend services
* Return structured responses

Main endpoints include:

* `/chat`
* `/upload`
* `/health`

---

## Chat Service

The chat service coordinates the question-answering workflow.

```text
Question
   ↓
Retrieval
   ↓
Context
   ↓
Prompt
   ↓
LLM
   ↓
Response
```

It acts as the service layer between the API and the RAG/LLM components.

---

## Document Processing Layer

This layer converts raw documents into searchable knowledge.

```text
Raw Document
     ↓
Loader
     ↓
Text Extraction
     ↓
Cleaning
     ↓
Chunking
     ↓
Embeddings
     ↓
Vector Storage
```

---

## RAG Layer

The RAG layer connects knowledge retrieval with AI generation.

Its responsibilities include:

* Query retrieval
* Vector search
* Relevant chunk selection
* Context retrieval
* Prompt construction

---

## LLM Layer

The LLM layer manages communication with the AI model.

Current implementation includes:

* OpenAI integration
* LLM request handling
* AI response generation

The LLM layer is separated from the RAG pipeline so the AI provider can be changed or extended later.

---

## Database Layer

The database layer manages persistent application data.

It includes:

* Database models
* Database sessions
* Base configuration
* Migrations
* Vector repository integration

---

# 10. API Overview

## Health Check

```text
GET /health
```

Used to verify that the backend service is running correctly.

---

## Chat

```text
POST /chat
```

Accepts a user question and returns a knowledge-grounded AI response.

Workflow:

```text
Question
   ↓
Retrieve
   ↓
Build Context
   ↓
Generate
   ↓
Response
```

---

## Document Upload

```text
POST /upload
```

Accepts documents and sends them through the document processing pipeline.

Workflow:

```text
Upload
   ↓
Extract
   ↓
Clean
   ↓
Chunk
   ↓
Embed
   ↓
Store
```

---

# 11. Configuration

Environment variables are used to keep sensitive configuration outside the source code.

Create a `.env` file based on:

```text
.env.example
```

Example:

```env
OPENAI_API_KEY=your_api_key
DATABASE_URL=your_database_url
VECTOR_DATABASE_URL=your_vector_database
```

Production credentials should never be committed to the repository.

---

# 12. Installation

## Clone Repository

```bash
git clone <repository-url>
```

Move into the project directory:

```bash
cd production-rag-api
```

## Create Virtual Environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 13. Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

---

# 14. Docker Deployment

The project includes Docker support for containerized deployment.

Build and start the application:

```bash
docker-compose up --build
```

Stop the services:

```bash
docker-compose down
```

Stop services and remove volumes:

```bash
docker-compose down -v
```

---

# 15. Design Principles

## Modularity

Each layer has a clearly defined responsibility, making the system easier to maintain and extend.

## Separation of Concerns

API, document processing, retrieval, database, and LLM logic are separated into independent components.

## Reusability

The backend is designed to serve multiple client applications instead of being tied to a single frontend.

## Scalability

The architecture provides a foundation for adding multiple knowledge bases, additional document types, improved retrieval strategies, and new AI capabilities.

## Security

Sensitive credentials are managed through environment variables and should not be exposed in application code.

---

# 16. Future Improvements

Potential improvements include:

* Multiple knowledge bases
* Multiple document types
* Streaming AI responses
* User authentication
* Role-based access control
* Usage analytics
* Retrieval evaluation
* Advanced metadata filtering
* Improved chunking strategies
* Retrieval quality optimization
* LLM provider abstraction
* Production monitoring and observability

---

# 17. License

MIT License

---

# Summary

**AI RAG Backend System** is a reusable production-oriented RAG infrastructure for building AI assistants that can work with private and domain-specific knowledge.

It combines:

* FastAPI
* Document processing
* Chunking
* Embeddings
* Vector search
* Retrieval pipelines
* Prompt construction
* OpenAI LLM integration
* Database persistence
* Docker-based deployment

The backend can operate as a centralized **Production RAG API**, allowing different applications to use the same retrieval and AI intelligence layer.

```text
                Production RAG API
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
    WordPress       Web App       Custom Client
    Assistant       Assistant         API
        │              │              │
        └──────────────┼──────────────┘
                       ↓
                RAG Intelligence
                       ↓
                    OpenAI
```
