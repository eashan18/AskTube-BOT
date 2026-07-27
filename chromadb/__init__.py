"""Lightweight local stub for chromadb used in tests.

This is NOT the real chromadb; it's a minimal in-memory shim to
allow unit tests to import the project's modules without installing
the full `chromadb` package.
"""
import json
import os
from typing import Any, Dict, List, Optional

_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "_persist")
_GLOBAL_COLLECTIONS: Dict[str, "Collection"] = {}


def _ensure_persist_dir():
    if not os.path.exists(_PERSIST_DIR):
        os.makedirs(_PERSIST_DIR, exist_ok=True)


def _persist_path(name: str) -> str:
    return os.path.join(_PERSIST_DIR, f"{name}.json")


def _load_collection_state(name: str) -> Optional[Dict[str, Any]]:
    path = _persist_path(name)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _save_collection_state(name: str, state: Dict[str, Any]) -> None:
    _ensure_persist_dir()
    with open(_persist_path(name), "w", encoding="utf-8") as handle:
        json.dump(state, handle)


def _matches_filter(metadata: Dict[str, Any], where: Optional[Dict[str, Any]]):
    if not where:
        return True
    # support simple equal filters: {"video_id": {"$eq": value}}
    for field, condition in where.items():
        if not isinstance(condition, dict):
            return False
        if "$eq" in condition:
            if metadata.get(field) != condition["$eq"]:
                return False
        else:
            return False
    return True


class Collection:
    def __init__(self, name: str):
        self.name = name
        self._ids: List[str] = []
        self._docs: List[str] = []
        self._metadatas: List[Dict[str, Any]] = []
        self._embeddings: List[List[float]] = []
        state = _load_collection_state(name)
        if state:
            self._ids = state.get("ids", [])
            self._docs = state.get("docs", [])
            self._metadatas = state.get("metadatas", [])
            self._embeddings = state.get("embeddings", [])

    def upsert(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]], embeddings: Optional[List[List[float]]] = None):
        # naive append/replace by id
        for i, _id in enumerate(ids):
            if _id in self._ids:
                idx = self._ids.index(_id)
                self._docs[idx] = documents[i]
                self._metadatas[idx] = metadatas[i]
                if embeddings:
                    self._embeddings[idx] = embeddings[i]
            else:
                self._ids.append(_id)
                self._docs.append(documents[i])
                self._metadatas.append(metadatas[i])
                if embeddings:
                    self._embeddings.append(embeddings[i])
        _save_collection_state(self.name, {
            "ids": self._ids,
            "docs": self._docs,
            "metadatas": self._metadatas,
            "embeddings": self._embeddings,
        })

    def query(self, query_embeddings=None, n_results: int = 5, where=None, include=None):
        # return top-n by insertion order (no real similarity)
        matched = [i for i, md in enumerate(self._metadatas) if _matches_filter(md, where)]
        n = min(n_results, len(matched))
        ids = [[self._ids[i] for i in matched[:n]]]
        documents = [[self._docs[i] for i in matched[:n]]]
        metadatas = [[self._metadatas[i] for i in matched[:n]]]
        distances = [[0.0] * n]
        embeddings = [[self._embeddings[i] for i in matched[:n]] if self._embeddings else []]
        return {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
            "distances": distances,
            "embeddings": embeddings,
        }


class Client:
    def __init__(self, settings: Any = None):
        self._collections: Dict[str, Collection] = _GLOBAL_COLLECTIONS

    def get_collection(self, name: str) -> Collection:
        if name in self._collections:
            return self._collections[name]
        # load persisted collection state lazily if available
        col = Collection(name)
        if col._ids or col._docs or col._metadatas or col._embeddings:
            self._collections[name] = col
            return col
        raise Exception("collection not found")

    def create_collection(self, name: str) -> Collection:
        col = Collection(name)
        self._collections[name] = col
        return col

    def persist(self):
        # persistent storage is handled by Collection.upsert
        return None
