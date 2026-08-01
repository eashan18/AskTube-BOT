# AskTube-BOT

A local FastAPI + Streamlit app for chatting with YouTube video transcripts (RAG). This repository is intended to run locally for development and testing.

Important: Do NOT expose your API keys or run the app in production without protecting endpoints and monitoring usage. See "Costs & Safety" below.

## Quick Local Run

1. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Start the backend (in one terminal)

```powershell
py -3 -m uvicorn backend.main:app --reload --port 8001
```

3. Start the Streamlit frontend (in another terminal)

```powershell
py -3 -m streamlit run frontend/streamlit_app.py
```

4. Open the app locally in your browser:

- Backend API: `http://localhost:8001`
- Frontend UI: `http://localhost:8501`

Note: `localhost` links only work on your machine. If you include them in the repo, other users cannot access your running app.

## Uploading & Chatting

- Use the "Upload Video" page in the Streamlit UI to index a YouTube video.
- Use the "Chat" page to ask questions about the indexed video.
- History is stored locally in the SQLite DB and is session-scoped by default (not shared via URL).

## Costs & Safety

- This project may call paid services (LLM APIs, embedding APIs, managed DBs). If you deploy or provide API keys, you will be billed by the provider for usage.
- Do not commit API keys or secrets to the repo. Use environment variables or your host's secrets manager.
- For public deployment, add authentication, rate limits, and a billing/usage cap on your LLM provider.

## Sharing the App

- To share publicly, deploy to a hosting provider (Streamlit Cloud, Render, AWS, etc.) — expect hosting and API costs.
- For a temporary public demo, you can use tools like `ngrok` to create a tunnel to your local `localhost:8501`, but this exposes your machine and should be used only temporarily.

## Want me to help?

I can:
- Add a minimal README with these steps (done).
- Add simple auth or API-key middleware to protect upload/chat endpoints.
- Add rate-limiting middleware and file-size limits for uploads.
- Create a GitHub Actions workflow to run tests.

Reply which of the above you'd like me to add next.AskTube AI — Chat with Any YouTube Video
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

    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001

    If port `8000` is already in use or not responding, use `8001` instead.

4. Run the Streamlit frontend:

    streamlit run frontend/streamlit_app.py

    If Streamlit cannot reach the backend, set the API base URL explicitly:

    - Windows (PowerShell): `setx API_BASE "http://localhost:8001/api"`
    - macOS/Linux: `export API_BASE="http://localhost:8001/api"`

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
