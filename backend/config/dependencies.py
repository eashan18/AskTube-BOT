"""Dependency helpers for FastAPI routes and services.

Provides `get_settings` and `get_db` (SQLAlchemy session) as DI providers.
"""
from functools import lru_cache
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .settings import get_settings, Settings


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
