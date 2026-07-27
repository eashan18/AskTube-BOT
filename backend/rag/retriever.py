"""RAG retriever: embed queries, retrieve relevant chunks from ChromaDB.

This module glues the embedding generation and `ChromaClient` to provide a
single `RAGRetriever` class used by services and API endpoints.
"""
from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional

from ..config.settings import get_settings
from .embeddings import embed_texts
from .chroma_db import ChromaClient

logger = logging.getLogger(__name__)


class RAGRetriever:
    """High-level retriever that returns Top-K MMR-ranked chunks for a query.

    Usage:
        retriever = RAGRetriever()
        results = retriever.retrieve(query, top_k=5, video_id=...)
    """

    def __init__(self, collection_name: str = "asktube_chunks"):
        self.settings = get_settings()
        self.chroma = ChromaClient(collection_name=collection_name)

    def retrieve(self, query: str, top_k: int | None = None, video_id: Optional[str] = None, lambda_mult: float = 0.5, candidate_pool: int = 50) -> List[Dict[str, Any]]:
        """Embed the `query` and retrieve the top-k results.

        If `video_id` is provided, a filter will be applied to only search that video.
        Returns a list of result dicts with `id`, `document`, `metadata`, `distance`, `embedding`.
        """
        top_k = int(top_k or self.settings.DEFAULT_TOP_K)

        logger.debug("Embedding the query for retrieval")
        q_embs = embed_texts([query], batch_size=1)
        if not q_embs:
            raise ValueError("Failed to generate embedding for query")

        q_emb = q_embs[0]

        filter_cond = None
        if video_id:
            filter_cond = {"video_id": {"$eq": video_id}}  # Chroma `where` filter syntax

        results = self.chroma.query(query_embedding=q_emb, top_k=top_k, lambda_mult=lambda_mult, filter=filter_cond, candidate_pool=candidate_pool)
        return results
