from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...config.dependencies import get_db
from ...schemas.api import UploadRequest, UploadResponse
from ...services.video_service import VideoService, VideoProcessingError

router = APIRouter()


@router.post("/upload-video", response_model=UploadResponse)
def upload_video(payload: UploadRequest, db: Session = Depends(get_db)):
    # instantiate service lazily to avoid heavy imports at module import time
    video_service = VideoService()
    try:
        res = video_service.process_and_index(db, payload.url)
    except VideoProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return UploadResponse(video_id=res["video_id"], title=res.get("title"), chunks_indexed=res.get("chunks_indexed", 0))
