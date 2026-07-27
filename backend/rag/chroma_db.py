"""ChromaDB client wrapper for persisting embeddings and retrieval.

Provides:
- `ChromaClient` class to create/get collection, add embeddings with metadata,
  and query via embedding with an MMR re-ranker.
"""
from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional

import numpy as np
import chromadb
from chromadb.config import Settings as ChromaSettings

from ..config.settings import get_settings

logger = logging.getLogger(__name__)


def _mmr(query_embedding: np.ndarray, candidate_embeddings: np.ndarray, candidate_ids: List[str], k: int = 5, lambda_mult: float = 0.5) -> List[int]:
    """Simple MMR (Maximal Marginal Relevance) selection.

    Returns indices into candidate_embeddings representing the selected items.
    """
    # cosine similarities
    if candidate_embeddings.size == 0:
        return []
    # normalize
    q = query_embedding / (np.linalg.norm(query_embedding) + 1e-12)
    C = candidate_embeddings / (np.linalg.norm(candidate_embeddings, axis=1, keepdims=True) + 1e-12)

    sims = (C @ q).tolist()
    selected = []
    selected_set = set()
    # select the highest similarity as first
    first = int(np.argmax(sims))
    selected.append(first)
    selected_set.add(first)

    while len(selected) < k and len(selected) < len(candidate_embeddings):
        mmr_scores = []
        for idx in range(len(candidate_embeddings)):
            if idx in selected_set:
                mmr_scores.append((-1e9, idx))
                continue
            relevance = sims[idx]
            # compute redundancy = max similarity to any selected
            redundancy = max((C[idx] @ C[s]).item() for s in selected)
            score = lambda_mult * relevance - (1 - lambda_mult) * redundancy
            mmr_scores.append((score, idx))

        # pick argmax score
        mmr_scores.sort(reverse=True)
        chosen_idx = mmr_scores[0][1]
        selected.append(chosen_idx)
        selected_set.add(chosen_idx)

    return selected


class ChromaClient:
    """Wrapper over chromadb client providing persistence and retrieval.

    Collections are created per project namespace (default 'asktube_chunks').
    """

    def __init__(self, collection_name: str = "asktube_chunks"):
        settings = get_settings()
        chroma_settings = ChromaSettings(chroma_db_impl="duckdb+parquet", persist_directory=settings.CHROMA_DB_DIR)
        self._client = chromadb.Client(chroma_settings)
        self.collection_name = collection_name
        self._collection = self._get_or_create_collection(collection_name)

    def _get_or_create_collection(self, name: str):
        try:
            return self._client.get_collection(name)
        except Exception:
            logger.info("Creating chroma collection: %s", name)
            return self._client.create_collection(name=name)

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]], ids: Optional[List[str]] = None) -> None:
        """Add chunk documents with embeddings and metadata.

        Args:
            chunks: list of dicts with at least `content` and `metadata` keys.
            embeddings: list of vector lists matching chunks order.
            ids: optional list of unique ids for each chunk. If None, generated.
        """
        if ids is None:
            ids = [f"{c['metadata']['video_id']}_chunk_{c['metadata']['chunk_number']}" for c in chunks]

        documents = [c.get("content") or c.get("original_text") or "" for c in chunks]
        metadatas = [c.get("metadata", {}) for c in chunks]

        # upsert with IDs
        try:
            self._collection.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
            # persist if supported
            try:
                self._client.persist()
            except Exception:
                # older chroma versions may persist automatically
                pass
        except Exception as exc:
            logger.exception("Failed to upsert chunks into ChromaDB: %s", exc)
            raise

    def query(self, query_embedding: List[float], top_k: int = 5, lambda_mult: float = 0.5, filter: Optional[Dict[str, Any]] = None, candidate_pool: int = 50) -> List[Dict[str, Any]]:
        """Retrieve top-k chunks using MMR re-ranking.

        Steps:
        1. Use Chroma to retrieve `candidate_pool` nearest neighbors.
        2. Apply MMR to select final `top_k` results.

        Returns a list of results containing `id`, `document`, `metadata`, `distance`, and `embedding` when available.
        """
        # initial candidate retrieval
        q_emb = query_embedding
        try:
            resp = self._collection.query(query_embeddings=[q_emb], n_results=candidate_pool, where=filter, include=["metadatas", "documents", "distances", "ids", "embeddings"])  # type: ignore[arg-type]
        except TypeError:
            # older chroma signature: collection.query(..., where=filter)
            resp = self._collection.query(query_embeddings=[q_emb], n_results=candidate_pool, where=filter, include=["metadatas", "documents", "distances", "ids"])  # type: ignore[arg-type]

        # response shapes are arrays per field
        ids = resp.get("ids", [[]])[0]
        documents = resp.get("documents", [[]])[0]
        metadatas = resp.get("metadatas", [[]])[0]
        distances = resp.get("distances", [[]])[0]
        embeddings = resp.get("embeddings", [[]])
        candidate_embeddings = None
        if embeddings and len(embeddings) > 0:
            candidate_embeddings = np.array(embeddings[0])
        else:
            # if chroma didn't return embeddings, we cannot run MMR; fallback to distances
            candidate_embeddings = None

        # If we have candidate embeddings, run MMR; else pick top_k by distance
        results: List[Dict[str, Any]] = []
        if candidate_embeddings is not None and len(candidate_embeddings) > 0:
            q_vec = np.array(q_emb)
            selected_idxs = _mmr(q_vec, candidate_embeddings, ids, k=top_k, lambda_mult=lambda_mult)
            for si in selected_idxs:
                results.append({
                    "id": ids[si],
                    "document": documents[si],
                    "metadata": metadatas[si],
                    "distance": float(distances[si]) if si < len(distances) else None,
                    "embedding": candidate_embeddings[si].tolist(),
                })
        else:
            # fallback by distances order
            for i in range(min(top_k, len(ids))):
                results.append({
                    "id": ids[i],
                    "document": documents[i],
                    "metadata": metadatas[i],
                    "distance": float(distances[i]) if i < len(distances) else None,
                    "embedding": None,
                })

        return results
