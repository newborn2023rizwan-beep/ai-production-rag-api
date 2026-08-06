# RAG Document Assistant — Backend

## Step 1 checkpoint: Database + Models + Docker setup

This checkpoint gives you:
- Postgres + pgvector running in Docker
- SQLAlchemy models for: documents, chunks, chat_sessions, messages,
  message_sources, settings
- A `/health` endpoint that confirms the backend can reach the database
- Swagger UI at `/docs`

### 1. Setup

```bash
cp .env.example .env
```
Open `.env` and set a real `POSTGRES_PASSWORD` (and update `DATABASE_URL`
to match). Leave the LLM/embedding keys blank for now — not needed until
later steps.

### 2. Start the containers

```bash
docker-compose up --build
```

This starts two services:
- `db` — Postgres 16 with pgvector, persisted in a Docker volume
- `backend` — the FastAPI app, live-reloading from your local `app/` folder

Wait until you see the backend log show Uvicorn running on port 8000.

### 3. Create the database tables

In a second terminal, with the containers still running:

```bash
docker-compose exec backend python scripts/create_db.py
```

You should see it enable the pgvector extension and list all 6 tables
being created.

### 4. Verify

- Open **http://localhost:8000/docs** — Swagger UI should load.
- Try the `/health` endpoint — it should return:
  ```json
  { "status": "ok", "database": "ok" }
  ```
  If `database` shows an error instead of `"ok"`, double check your `.env`
  values match what's in `docker-compose.yml`.

- Optional: connect directly to Postgres to see the tables yourself:
  ```bash
  docker-compose exec db psql -U raguser -d rag_db -c "\dt"
  ```
  (replace `raguser` with whatever you set as `POSTGRES_USER`)

### What's NOT built yet (by design)

Everything under `document_processing/`, `rag/`, `llm/`, `chat/`, and most
of `api/` is intentionally not implemented yet. Those come in the next
steps (PDF upload → chunking → embeddings → retrieval → chat), each
delivered as a working addition on top of this same project.

### Stopping

```bash
docker-compose down       # stops containers, keeps DB data
docker-compose down -v    # stops containers AND wipes DB data
```
