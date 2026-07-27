import numpy as np

import backend.rag.embeddings as embeddings


class DummyModel:
    def encode(self, texts, convert_to_numpy=True):
        # return a simple deterministic vector based on index
        arr = np.array([[float(len(t)), float(len(t)), float(len(t))] for t in texts])
        return arr


def test_embed_texts_monkeypatch_model(monkeypatch):
    dummy = DummyModel()
    # patch the cached model
    embeddings._MODEL = dummy

    texts = ["hello", "world!!"]
    embs = embeddings.embed_texts(texts, batch_size=1)
    assert isinstance(embs, list)
    assert len(embs) == 2
    assert all(isinstance(v, list) for v in embs)
    assert embs[0][0] == float(len(texts[0]))
