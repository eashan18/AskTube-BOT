import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.config.settings import get_settings
from backend.services.video_service import VideoService, VideoProcessingError

settings = get_settings()

def make_db_session():
    url = settings.SQLALCHEMY_DATABASE_URL or settings.DATABASE_URL
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    engine = create_engine(url, connect_args=connect_args, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)
    return SessionLocal()

if __name__ == '__main__':
    db = make_db_session()
    svc = VideoService()
    try:
        res = svc.process_and_index(db, 'ENLEjGozrio')
        print('RESULT', res)
    except VideoProcessingError as e:
        print('VideoProcessingError:', e)
    except Exception:
        traceback.print_exc()
