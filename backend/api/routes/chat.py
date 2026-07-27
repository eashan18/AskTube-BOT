from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...config.dependencies import get_db
from ...schemas.api import ChatRequest, ChatResponse
from ...services.chat_service import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    # instantiate ChatService lazily to avoid heavy imports at module import time
    chat_service = ChatService()
    try:
        res = chat_service.answer(db, question=payload.question, video_id=payload.video_id, top_k=payload.top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return ChatResponse(answer=res["answer"], citations=res["citations"], retrieved_chunks=res["retrieved_chunks"])
