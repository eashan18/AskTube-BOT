from __future__ import annotations

from datetime import datetime
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
    user_id: Optional[str] = None


class ChatHistoryItem(BaseModel):
    user_id: Optional[str] = None
    video_id: Optional[str] = None
    question: str
    answer: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    items: List[ChatHistoryItem]


class ChatResponse(BaseModel):
    answer: str
    citations: List[Any]
    retrieved_chunks: List[Any]
