"""Minimal chromadb.config.Settings shim for tests."""
from dataclasses import dataclass


@dataclass
class Settings:
    chroma_db_impl: str = "duckdb+parquet"
    persist_directory: str | None = None
