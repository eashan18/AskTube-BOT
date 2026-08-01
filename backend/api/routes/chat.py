from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ...config.dependencies import get_db
from ...schemas.api import ChatRequest, ChatResponse, ChatHistoryResponse
from ...services.chat_service import ChatService
from ...database import repository as repo

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    # instantiate ChatService lazily to avoid heavy imports at module import time
    chat_service = ChatService()
    try:
        res = chat_service.answer(
            db,
            question=payload.question,
            video_id=payload.video_id,
            top_k=payload.top_k,
            user_id=payload.user_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return ChatResponse(answer=res["answer"], citations=res["citations"], retrieved_chunks=res["retrieved_chunks"])


@router.get("/chat-history", response_model=ChatHistoryResponse)
def chat_history(user_id: str = Query(...), video_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    items = repo.get_chat_history(db, user_id=user_id, video_id=video_id)
    return ChatHistoryResponse(items=[
        {
            "user_id": item.user_id,
            "video_id": item.video_id,
            "question": item.question,
            "answer": item.answer,
            "created_at": item.created_at,
        }
        for item in items
    ])
