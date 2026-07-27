"""Embedding utilities using `sentence-transformers`.

Provides a cached model loader and batched embedding generation compatible
with ChromaDB storage (lists of floats).
"""
from __future__ import annotations

from typing import List, Iterable
import logging

import numpy as np
from sentence_transformers import SentenceTransformer

from ..config.settings import get_settings

logger = logging.getLogger(__name__)


_MODEL = None


def load_embedding_model(model_name: str | None = None) -> SentenceTransformer:
    """Load and cache a SentenceTransformer embedding model.

    Args:
        model_name: Optional model identifier. Falls back to settings.EMBEDDING_MODEL.
    """
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    settings = get_settings()
    model_name = model_name or settings.EMBEDDING_MODEL
    logger.info("Loading embedding model: %s", model_name)
    try:
        _MODEL = SentenceTransformer(model_name)
    except Exception as exc:
        logger.exception("Failed to load embedding model %s", model_name)
        raise
    return _MODEL


def embed_texts(texts: Iterable[str], batch_size: int | None = None) -> List[List[float]]:
    """Generate embeddings for an iterable of texts in batches.

    Returns a list of lists (float vectors) in the same order as `texts`.
    """
    model = load_embedding_model()
    settings = get_settings()
    batch_size = int(batch_size or settings.EMBEDDING_BATCH_SIZE)

    embeddings: List[List[float]] = []
    buffer = []
    count = 0
    for txt in texts:
        buffer.append(txt)
        count += 1
        if len(buffer) >= batch_size:
            emb = model.encode(buffer, convert_to_numpy=True)
            # ensure Python native floats for JSON/storage compatibility
            embeddings.extend([list(map(float, v)) for v in emb.tolist()])
            buffer = []

    if buffer:
        emb = model.encode(buffer, convert_to_numpy=True)
        embeddings.extend([list(map(float, v)) for v in emb.tolist()])

    return embeddings


def embed_chunks(chunks: List[dict], text_key: str = "content") -> List[List[float]]:
    """Convenience helper to embed a list of chunk dicts, extracting `text_key`.

    Keeps ordering and returns embeddings aligned to `chunks`.
    """
    texts = [c.get(text_key, "") for c in chunks]
    return embed_texts(texts)
