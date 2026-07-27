from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class TranscriptSegment(BaseModel):
    text: str
    start: float
    duration: Optional[float] = None


class VideoMetadata(BaseModel):
    video_id: str
    title: str
    channel: Optional[str] = None
    thumbnail: Optional[HttpUrl] = None
    duration: Optional[float] = None


class VideoTranscript(BaseModel):
    metadata: VideoMetadata
    segments: List[TranscriptSegment]
    full_text: str
    extracted_at: datetime = datetime.utcnow()
