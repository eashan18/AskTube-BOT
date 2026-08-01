from functools import lru_cache
from pathlib import Path
from typing import Optional
import os

try:
    from pydantic import BaseSettings, Field, AnyUrl
except Exception:
    try:
        # pydantic v2 moved BaseSettings to pydantic-settings package
        from pydantic_settings import BaseSettings  # type: ignore
        from pydantic import Field, AnyUrl  # type: ignore
    except Exception:
        # Last-resort shim for environments without pydantic available
        def Field(default, **kwargs):
            return default

        class BaseSettings:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        AnyUrl = str


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Uses pydantic BaseSettings to provide typed configuration and `.env` support.
    """

    # App
    APP_ENV: str = Field("development", env="APP_ENV")
    DEBUG: bool = Field(True, env="DEBUG")
    PORT: int = Field(8000, env="PORT")

    # Database
    DATABASE_URL: str = Field("sqlite:///./asktube.db", env="DATABASE_URL")
    SQLALCHEMY_DATABASE_URL: str = Field("sqlite:///./asktube.db", env="SQLALCHEMY_DATABASE_URL")

    # ChromaDB
    CHROMA_DB_DIR: str = Field("./data/chroma", env="CHROMA_DB_DIR")
    CHROMA_PERSIST: bool = Field(True, env="CHROMA_PERSIST")

    # Embeddings
    EMBEDDING_MODEL: str = Field("BAAI/bge-small-en-v1.5", env="EMBEDDING_MODEL")
    EMBEDDING_BATCH_SIZE: int = Field(32, env="EMBEDDING_BATCH_SIZE")

    # LLM / API keys
    GROQ_API_KEY: Optional[str] = Field(None, env="GROQ_API_KEY")
    GROQ_BASE_URL: str = Field("https://api.groq.com", env="GROQ_BASE_URL")
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")

    # Whisper & tools
    WHISPER_MODEL: str = Field("small", env="WHISPER_MODEL")
    FORCE_WHISPER_TRANSCRIPTION: bool = Field(False, env="FORCE_WHISPER_TRANSCRIPTION")
    FFMPEG_PATH: str = Field("ffmpeg", env="FFMPEG_PATH")
    YTDLP_PATH: str = Field("yt-dlp", env="YTDLP_PATH")

    # Defaults
    DEFAULT_TOP_K: int = Field(5, env="DEFAULT_TOP_K")
    CHUNK_SIZE: int = Field(1000, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(200, env="CHUNK_OVERLAP")
    TEMPERATURE: float = Field(0.0, env="TEMPERATURE")
    MAX_TOKENS: int = Field(1024, env="MAX_TOKENS")

    # File storage
    UPLOAD_DIR: str = Field("./data/uploads", env="UPLOAD_DIR")
    EMBEDDING_INDEX_DIR: str = Field("./data/chroma", env="EMBEDDING_INDEX_DIR")
    LOG_DIR: str = Field("./logs", env="LOG_DIR")

    # Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    if hasattr(BaseSettings, "model_config"):
        model_config = {
            "env_file": ".env",
            "env_file_encoding": "utf-8",
        }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def _load_env_file() -> None:
    env_path = Path(".env")
    if env_path.exists():
        with env_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if "=" not in stripped:
                    continue
                key, value = stripped.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                existing = os.environ.get(key)
                if key and (existing is None or existing == ""):
                    os.environ[key] = value


@lru_cache()
def get_settings() -> Settings:
    """Return a cached `Settings` instance.

    Use this in dependency injection to avoid recreating Settings objects.
    """
    _load_env_file()
    return Settings()
