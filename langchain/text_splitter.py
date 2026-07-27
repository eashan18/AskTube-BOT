"""Minimal text splitter shim compatible with the project's usage.

Implements `RecursiveCharacterTextSplitter` with a `split_text()` method.
This is intentionally simple and only used for unit tests when the
real `langchain` package is not installed.
"""
from typing import List


class RecursiveCharacterTextSplitter:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, separators=None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]

    def split_text(self, text: str) -> List[str]:
        if not text:
            return []
        chunks = []
        i = 0
        L = len(text)
        while i < L:
            end = i + self.chunk_size
            chunk = text[i:end]
            chunks.append(chunk.strip())
            i = end - self.chunk_overlap
            if i < 0:
                i = 0
        return [c for c in chunks if c]
