# AskTube AI — Architecture

This document describes the high-level architecture for AskTube AI.

Overview
--------

1. User pastes a YouTube URL in the Streamlit frontend.
2. Frontend calls FastAPI `POST /api/upload-video`.
3. Backend extracts transcript (youtube-transcript-api or Whisper fallback), cleans and chunks it.
4. Chunks are embedded using `sentence-transformers` and stored in ChromaDB with metadata.
5. When a user asks a question, the backend embeds the query, retrieves candidate chunks via Chroma, re-ranks using MMR, and builds a strict prompt.
6. The LLM (Groq primary) is called with the prompt. Responses are constrained to the provided context.
7. The answer, citations, and retrieved chunk references are returned to the UI and stored in chat history (SQLite).

Architecture Diagram (Mermaid)

```mermaid
flowchart LR
  subgraph UI
    A[Streamlit Frontend]
  end

  subgraph API
    B[FastAPI]
  end

  subgraph Processing
    C[TranscriptService]\n(YouTube Transcript / Whisper)
    D[Chunker]
    E[Embedding Model]\n(BAAI/bge-small-en-v1.5)
    F[ChromaDB]\n(duckdb+parquet)
    G[MMR Retriever]
    H[LLM Client]\n(Groq)
  end

  A -->|upload URL / ask question| B
  B --> C --> D --> E --> F
  B --> G --> H --> B
  G --> F
  A <-- B

```

Data Stores
-----------

- ChromaDB: vector index with chunk metadata (video_id, chunk number, timestamps, original text).
- SQLite: metadata for videos and chat history.

Security & Operations
---------------------

- Environment variables contain API keys and configuration (`.env` with `python-dotenv`).
- Logging configured in `backend/config/logging_config.py` and used via `backend/core/logger.py`.
- Docker and docker-compose provided for containerized deployment.
