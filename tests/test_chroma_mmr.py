import numpy as np

from backend.rag.chroma_db import _mmr


def test_mmr_selection_simple():
    # candidate embeddings: first is identical to query, second similar, third different
    candidate_embeddings = np.array([[1.0, 0.0, 0.0], [0.9, 0.1, 0.0], [0.0, 1.0, 0.0]])
    candidate_ids = ["a", "b", "c"]
    query = np.array([1.0, 0.0, 0.0])
    selected = _mmr(query, candidate_embeddings, candidate_ids, k=2, lambda_mult=0.5)
    assert len(selected) == 2
    assert 0 in selected
