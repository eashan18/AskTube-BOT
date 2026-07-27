AskTube AI — Chat with Any YouTube Video
========================================

AskTube AI is a production-grade Retrieval-Augmented Generation (RAG) application that lets users paste YouTube URLs, automatically extract transcripts, build a vector index, and ask questions that are answered strictly from the uploaded video content.

Features
--------
- Paste a YouTube URL and extract transcripts (youtube-transcript-api with Whisper fallback).
- Clean and chunk transcripts into semantic pieces.
- Generate embeddings with sentence-transformers (BAAI/bge-small-en-v1.5).
- Persist embeddings and metadata in ChromaDB (persistent storage).
- Serve a FastAPI backend and Streamlit frontend.
- Strict prompt templates to prevent hallucinations; responses must come from retrieved context.
- SQLite metadata and chat history storage.

Repository layout
-----------------

- backend/ — FastAPI app, services, RAG logic, DB models
- frontend/ — Streamlit UI (streamlit_app.py)
- docs/ — architecture and deployment notes
- tests/ — pytest unit tests
- Dockerfile, docker-compose.yml — containerization
- requirements.txt, .env.example

Getting started (local)
-----------------------

1. Create a Python 3.11+ virtual environment and install dependencies:

    python -m venv .venv
    source .venv/bin/activate   # or .venv\Scripts\activate on Windows
    pip install --upgrade pip
    pip install -r requirements.txt

2. Copy `.env.example` to `.env` and fill in keys (notably `GROQ_API_KEY` and `OPENAI_API_KEY` if used):

    cp .env.example .env
    # then edit .env to add API keys

3. Run the FastAPI backend:

    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

4. Run the Streamlit frontend:

    streamlit run frontend/streamlit_app.py

Docker (recommended for production-like runs)
-------------------------------------------

Build and start both services using Docker Compose:

    docker compose up --build

API Endpoints (overview)
------------------------

- POST /api/upload-video — body { "url": "<youtube_url>" } — extracts transcript, chunks, embeds, indexes.
- POST /api/chat — body { "question": "...", "video_id": "<optional>", "top_k": 5 } — returns an answer with citations and retrieved chunks.
- GET /api/health — health check.

Testing
-------

Run tests with pytest:

    pytest -q

Notes & operational details
---------------------------

- The project uses Chroma (duckdb+parquet) for persistent vector storage.
- ffmpeg is required for Whisper audio processing if using the fallback.
- The prompt templates in `backend/rag/prompts.py` strictly instruct the LLM to answer only from retrieved context and to reply with "I couldn't find that information in the uploaded video." if content is missing.

Security & credentials
----------------------

- Keep API keys out of source control; use environment variables or secrets manager.

Future improvements
-------------------

- Add user authentication and per-user collections.
- Background processing worker for long-running indexing (Celery, RQ, or FastAPI BackgroundTasks).
- Pagination and search across metadata (titles, channels).
- Add model orchestration and provider fallback (Groq -> OpenAI -> local LLM).
- Add end-to-end integration tests and CI pipeline.

See docs/architecture.md for the architecture diagram and more details.
