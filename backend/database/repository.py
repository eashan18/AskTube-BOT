from __future__ import annotations

import json
from typing import List, Optional
from sqlalchemy.orm import Session

from .models import Video, Chunk, ChatHistory


def create_video(db: Session, video_id: str, title: str, channel: Optional[str], thumbnail: Optional[str], duration: Optional[float], transcript: Optional[str], transcript_extracted_at=None) -> Video:
    video = Video(
        id=video_id,
        title=title,
        channel=channel,
        thumbnail=thumbnail,
        duration=duration,
        transcript=transcript,
        transcript_extracted_at=transcript_extracted_at,
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


def get_video(db: Session, video_id: str) -> Optional[Video]:
    return db.query(Video).filter(Video.id == video_id).first()


def list_videos(db: Session, limit: int = 100) -> List[Video]:
    return db.query(Video).limit(limit).all()


def delete_video(db: Session, video_id: str) -> bool:
    v = get_video(db, video_id)
    if not v:
        return False
    db.delete(v)
    db.commit()
    return True


def add_chunks(db: Session, video_id: str, chunks: List[dict]):
    # chunks: list of dicts with chunk_number, start_timestamp, end_timestamp, original_text
    # avoid inserting duplicate chunks (id unique constraint)
    existing = db.query(Chunk).filter(Chunk.video_id == video_id).all()
    existing_ids = {c.id for c in existing}

    objs = []
    for c in chunks:
        cid = f"{video_id}_chunk_{c['metadata']['chunk_number']}"
        if cid in existing_ids:
            # skip already-inserted chunk
            continue
        obj = Chunk(
            id=cid,
            video_id=video_id,
            chunk_number=c['metadata']['chunk_number'],
            start_timestamp=c['metadata']['start_timestamp'],
            end_timestamp=c['metadata']['end_timestamp'],
            text=c['content'],
        )
        objs.append(obj)
        db.add(obj)

    if objs:
        db.commit()
    # update chunk count
    video = get_video(db, video_id)
    if video:
        # update chunk_count to reflect total stored chunks for this video
        total_chunks = db.query(Chunk).filter(Chunk.video_id == video_id).count()
        video.chunk_count = total_chunks
        db.add(video)
        db.commit()


def get_chat_history(db: Session, user_id: str, video_id: Optional[str] = None, limit: int = 50) -> List[ChatHistory]:
    query = db.query(ChatHistory).filter(ChatHistory.user_id == user_id)
    if video_id:
        query = query.filter(ChatHistory.video_id == video_id)
    return query.order_by(ChatHistory.created_at.desc()).limit(limit).all()


def save_chat_history(db: Session, question: str, answer: str, retrieved_chunks: List[dict], user_id: Optional[str] = None, video_id: Optional[str] = None) -> ChatHistory:
    item = ChatHistory(
        user_id=user_id,
        video_id=video_id,
        question=question,
        answer=answer,
        retrieved_chunks=json.dumps(retrieved_chunks),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
