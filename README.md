<img width="1510" height="453" alt="image" src="https://github.com/user-attachments/assets/5e098f4e-6a4b-402d-900a-76ddb115aff7" /># AskTube-BOT

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

# AskTube-BOT

Project Overview
----------------
AskTube-BOT is a local prototype that lets you index YouTube videos (transcripts) and ask questions using a retrieval-augmented approach. It uses a FastAPI backend for indexing and search and a Streamlit frontend for interaction.

Demo Screenshot / GIF
<img width="1530" height="457" alt="image" src="https://github.com/user-attachments/assets/c740b654-0411-48d1-bffe-38bcc74b0856" />
---------------------


Features
--------
- Upload and index YouTube videos (transcript extraction and chunking)
- Vector embedding and retrieval for RAG-style Q&A
- Streamlit UI for upload, chat, and session history
- Local persistence with SQLite and optional Chroma embeddings

Architecture Diagram
--------------------
Add an architecture diagram at `docs/architecture.png` showing: Streamlit frontend → FastAPI backend → (Transcription / Embeddings / Chroma DB / SQLite).

Tech Stack
----------
- Python 3.10+
- FastAPI (backend)
- Streamlit (frontend)
- SQLite (local metadata)
- Chroma or local embedding index
- yt-dlp, youtube_transcript_api, Whisper (fallback)
- Embedding model: BAAI/bge-small-en-v1.5 (configurable)

Project Workflow
----------------
1. Upload a YouTube URL via the Streamlit UI.
2. Backend extracts/transcribes captions (YouTube API or Whisper fallback).
3. Backend splits and indexes chunks, computes embeddings, and persists metadata.
4. User asks questions in the Chat UI; backend retrieves relevant chunks and calls the LLM to generate answers.

Installation
------------
Windows PowerShell example:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run backend in one terminal
py -3 -m uvicorn backend.main:app --reload --port 8001

# Run frontend in another terminal
py -3 -m streamlit run frontend/streamlit_app.py

# Backend: http://localhost:8001
# Frontend: http://localhost:8501
```

Notes
- Copy `.env.example` to `.env` and set `GROQ_API_KEY` / `OPENAI_API_KEY` if required. Do NOT commit `.env`.

Future Improvements
-------------------
- Add authentication and rate limiting for public deployments
- Add CI (GitHub Actions) to run tests and linters
- Improve deployment docs and add a production configuration
- Add integration tests for `/api/chat-history` and upload flow

License
-------
MIT License — see `LICENSE`.

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
