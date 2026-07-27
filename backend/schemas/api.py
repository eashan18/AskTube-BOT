from __future__ import annotations

from typing import Optional, List, Any
from pydantic import BaseModel


class UploadRequest(BaseModel):
    url: str


class UploadResponse(BaseModel):
    video_id: str
    title: str
    chunks_indexed: int


class ChatRequest(BaseModel):
    question: str
    video_id: Optional[str] = None
    top_k: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    citations: List[Any]
    retrieved_chunks: List[Any]
