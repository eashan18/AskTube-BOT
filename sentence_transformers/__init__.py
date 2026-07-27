"""Tiny local stub for `sentence_transformers.SentenceTransformer` used in tests.

The real package is heavy; this stub returns deterministic zero vectors
and matches the minimal interface used by the project's code.
"""
import numpy as np


class SentenceTransformer:
    def __init__(self, model_name: str = None):
        self.model_name = model_name
        self._dim = 8

    def encode(self, texts, convert_to_numpy: bool = True):
        # Return a numpy array of shape (len(texts), dim)
        n = len(texts)
        arr = np.zeros((n, self._dim), dtype=float)
        return arr
