"""Transcript extraction service.

Provides functionality to extract transcripts from YouTube using
`youtube_transcript_api` with an OpenAI Whisper fallback.
"""
from __future__ import annotations

import logging
import os
import tempfile
from typing import List

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

from ..schemas.video import TranscriptSegment, VideoMetadata, VideoTranscript
from ..utils.text import clean_text, join_segments
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


def _get_video_id(url: str) -> str:
    # Support full URLs and bare IDs
    if "youtube.com" in url or "youtu.be" in url:
        # naive extraction: last path segment or v= param
        if "v=" in url:
            return url.split("v=")[-1].split("&")[0]
        else:
            return url.rstrip("/\n ").split("/")[-1]
    return url


class TranscriptService:
    """Service to fetch and clean transcripts for YouTube videos.

    Methods:
    - `extract_transcript_from_youtube(url)` -> VideoTranscript
    """

    PREFERRED_LANGUAGE_CODES = ["hi", "en"]

    def __init__(self):
        self.settings = get_settings()

    def _fetch_preferred_transcript(self, transcripts):
        if hasattr(transcripts, "find_transcript"):
            try:
                return transcripts.find_transcript(self.PREFERRED_LANGUAGE_CODES).fetch()
            except Exception:
                pass

        for language_code in self.PREFERRED_LANGUAGE_CODES:
            for transcript in transcripts:
                if getattr(transcript, "language_code", None) == language_code:
                    try:
                        return transcript.fetch()
                    except Exception:
                        continue

        for transcript in transcripts:
            try:
                return transcript.fetch()
            except Exception:
                continue

        return []

    def _fetch_transcript_with_preferred_languages(self, api, video_id: str):
        raw = []

        if hasattr(api, "list_transcripts"):
            transcripts = api.list_transcripts(video_id)
            raw = self._fetch_preferred_transcript(transcripts)
            if raw:
                return raw

        if hasattr(api, "list"):
            transcripts = api.list(video_id)
            raw = self._fetch_preferred_transcript(transcripts)
            if raw:
                return raw

        if hasattr(api, "get_transcript"):
            raw = api.get_transcript(video_id)
        elif hasattr(api, "get_transcripts"):
            raw = api.get_transcripts(video_id)
        elif hasattr(api, "fetch"):
            try:
                raw = api.fetch(video_id)
            except Exception:
                raw = []
        else:
            raise AttributeError("youtube_transcript_api missing expected API")

        return raw

    def extract_transcript_from_youtube(self, url: str) -> VideoTranscript:
        """Extract transcript using YouTube captions or direct audio speech transcription."""
        video_id = _get_video_id(url)

        if self.settings.FORCE_WHISPER_TRANSCRIPTION:
            logger.info("Force Whisper transcription enabled for video %s", video_id)
            try:
                return self._whisper_fallback(url, video_id)
            except Exception as exc:
                logger.exception(
                    "Forced Whisper transcription failed for %s, falling back to youtube_transcript_api: %s",
                    video_id,
                    exc,
                )

        try:
            api = YouTubeTranscriptApi()
            raw = self._fetch_transcript_with_preferred_languages(api, video_id)
        except (TranscriptsDisabled, NoTranscriptFound) as exc:
            logger.warning(
                "Transcript unavailable for video %s (%s), attempting list_transcripts/Whisper fallback",
                video_id,
                type(exc).__name__,
            )
            raw = []
            try:
                api = YouTubeTranscriptApi()
                if hasattr(api, "list_transcripts"):
                    transcripts = api.list_transcripts(video_id)
                    raw = self._fetch_preferred_transcript(transcripts)
                elif hasattr(api, "list"):
                    transcripts = api.list(video_id)
                    raw = self._fetch_preferred_transcript(transcripts)
            except Exception:
                raw = []
        except AttributeError as e:
            logger.error("youtube_transcript_api API not compatible: %s", e)
            raise RuntimeError(f"Transcript API not available for video {video_id}") from e
        except Exception as e:
            logger.exception("Unexpected error when fetching transcript: %s", e)
            raise RuntimeError(f"Failed to fetch transcript for {video_id}") from e

        # If the youtube_transcript_api returned nothing, attempt Whisper fallback
        if not raw:
            logger.info("Transcript unavailable via youtube_transcript_api, attempting Whisper fallback")
            try:
                return self._whisper_fallback(url, video_id)
            except Exception as exc:
                logger.exception("Whisper fallback failed: %s", exc)
                raise

        segments: List[TranscriptSegment] = []
        for seg in raw:
            text = clean_text(
                seg.get("text", "") if isinstance(seg, dict) else getattr(seg, "text", "")
            )
            start = float(
                seg.get("start", 0.0)
                if isinstance(seg, dict)
                else getattr(seg, "start", 0.0)
            )
            duration = float(
                seg.get("duration", 0.0)
                if isinstance(seg, dict)
                else getattr(seg, "duration", 0.0)
            )
            if not text:
                continue
            segments.append(TranscriptSegment(text=text, start=start, duration=duration))

        full_text = join_segments([{"text": s.text} for s in segments])

        # Note: youtube-transcript-api does not provide title/channel/thumbnail
        metadata = VideoMetadata(video_id=video_id, title=video_id)

        return VideoTranscript(metadata=metadata, segments=segments, full_text=full_text)

    def _whisper_fallback(self, url: str, video_id: str) -> VideoTranscript:
        """Download audio with yt-dlp and transcribe using OpenAI Whisper (if available).

        Returns a VideoTranscript built from Whisper segments.
        """
        settings = self.settings
        import yt_dlp
        import shutil

        tmpdir = tempfile.mkdtemp()
        out_path = os.path.join(tmpdir, f"{video_id}.wav")
        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": out_path,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "restrictfilenames": True,
            "ignoreerrors": False,
            "nocheckcertificate": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            },
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            shutil.rmtree(tmpdir, ignore_errors=True)
            logger.exception("yt-dlp audio download failed: %s", e)
            raise

        try:
            import whisper
        except Exception as e:
            shutil.rmtree(tmpdir, ignore_errors=True)
            logger.exception("whisper package not available: %s", e)
            raise

        try:
            model = whisper.load_model(settings.WHISPER_MODEL)
            result = model.transcribe(out_path)
        except Exception as e:
            shutil.rmtree(tmpdir, ignore_errors=True)
            logger.exception("Whisper transcription failed: %s", e)
            raise

        segments = []
        for seg in result.get("segments", []):
            text = clean_text(seg.get("text", ""))
            start = float(seg.get("start", 0.0))
            duration = float(seg.get("end", start) - start)
            if not text:
                continue
            segments.append(TranscriptSegment(text=text, start=start, duration=duration))

        full_text = join_segments([{"text": s.text} for s in segments])
        metadata = VideoMetadata(video_id=video_id, title=video_id)

        shutil.rmtree(tmpdir, ignore_errors=True)
        return VideoTranscript(metadata=metadata, segments=segments, full_text=full_text)
