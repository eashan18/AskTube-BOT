"""High-level video processing service: metadata, transcript, chunking, embeddings, indexing."""
from __future__ import annotations

import logging
from typing import Dict, Any, List
from urllib.parse import urlparse, parse_qs

from yt_dlp import YoutubeDL

from ..services.transcript_service import TranscriptService
from ..rag.chunker import chunk_transcript
from ..rag.embeddings import embed_chunks
from ..rag.chroma_db import ChromaClient
from ..database import repository as repo
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class VideoProcessingError(Exception):
    pass


class VideoService:
    def __init__(self):
        self.transcript_svc = TranscriptService()
        self.settings = get_settings()
        self.chroma = ChromaClient()

    def _normalize_url(self, url: str) -> str:
        """Normalize a YouTube URL to a single-video URL and strip playlist/query params."""
        parsed = urlparse(url)
        if parsed.netloc and "youtube" in parsed.netloc.lower():
            query = parse_qs(parsed.query)
            if "v" in query and query["v"]:
                return f"https://www.youtube.com/watch?v={query['v'][0]}"
        if parsed.netloc and "youtu.be" in parsed.netloc.lower():
            video_id = parsed.path.strip("/")
            if video_id:
                return f"https://www.youtube.com/watch?v={video_id}"
        return url

    def _extract_metadata(self, url: str) -> Dict[str, Any]:
        normalized_url = self._normalize_url(url)
        ydl_opts = {"quiet": True, "skip_download": True, "noplaylist": True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(normalized_url, download=False)
        return info

    def process_and_index(self, db, url: str) -> Dict[str, Any]:
        # extract metadata
        try:
            info = self._extract_metadata(url)
        except Exception as exc:
            logger.exception("Failed to extract video info: %s", exc)
            raise VideoProcessingError("Failed to extract video metadata")

        video_id = info.get("id")
        title = info.get("title") or video_id
        channel = info.get("uploader") or info.get("channel")
        thumbnail = info.get("thumbnail")
        duration = info.get("duration")

        # extract transcript
        try:
            vt = self.transcript_svc.extract_transcript_from_youtube(url)
        except Exception as exc:
            logger.exception("Transcript extraction failed: %s", exc)
            raise VideoProcessingError("Transcript extraction failed")

        # override metadata fields from yt-dlp
        vt.metadata.title = title
        vt.metadata.channel = channel

        # chunk transcript
        chunks = chunk_transcript(vt, chunk_size=self.settings.CHUNK_SIZE, chunk_overlap=self.settings.CHUNK_OVERLAP)

        # generate embeddings
        embeddings = embed_chunks(chunks)

        # upsert into chroma
        ids = [f"{video_id}_chunk_{c['metadata']['chunk_number']}" for c in chunks]
        self.chroma.add_chunks(chunks=chunks, embeddings=embeddings, ids=ids)

        # persist metadata and chunks to DB
        existing = repo.get_video(db, video_id)
        if not existing:
            repo.create_video(db, video_id=video_id, title=title, channel=channel, thumbnail=thumbnail, duration=duration, transcript=vt.full_text, transcript_extracted_at=vt.extracted_at)
        repo.add_chunks(db, video_id=video_id, chunks=chunks)

        return {"video_id": video_id, "title": title, "chunks_indexed": len(chunks)}
