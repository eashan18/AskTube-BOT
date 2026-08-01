"""Dependency helpers for FastAPI routes and services.

Provides `get_settings` and `get_db` (SQLAlchemy session) as DI providers.
"""
from functools import lru_cache
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from .settings import get_settings, Settings
from ..database.models import Base


@lru_cache()
def _create_engine():
    settings = get_settings()
    url = settings.SQLALCHEMY_DATABASE_URL or settings.DATABASE_URL
    connect_args = {}
    if url.startswith("sqlite"):
        # sqlite should disable same_thread check in multi-threaded servers
        connect_args = {"check_same_thread": False}

    engine = create_engine(url, connect_args=connect_args, future=True)
    return engine


def initialize_database() -> None:
    engine = _create_engine()
    Base.metadata.create_all(engine)

    # Migrate existing SQLite schema to include the user_id column for history.
    if str(engine.url).startswith("sqlite"):
        with engine.connect() as conn:
            rows = conn.execute(text("PRAGMA table_info(chat_history);")).all()
            if rows and not any(row[1] == "user_id" for row in rows):
                conn.execute(text("ALTER TABLE chat_history ADD COLUMN user_id VARCHAR"))
                conn.commit()


def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session for request-scoped operations.

    This is intended to be used as a FastAPI dependency:

        db: Session = Depends(get_db)

    The engine is cached via `_create_engine()`.
    """
    engine = _create_engine()
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
