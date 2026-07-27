"""Text utilities for cleaning transcripts."""
import re
from typing import Iterable, List


_WHITESPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Clean a block of transcript text.

    - Normalize whitespace
    - Remove non-printable/control characters
    - Strip leading/trailing whitespace
    """
    if not text:
        return ""
    # Remove control chars
    text = "".join(ch for ch in text if ch.isprintable())
    # Normalize whitespace
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def join_segments(segments: Iterable[dict], separator: str = " \n") -> str:
    """Join transcript segments into a single cleaned text block.

    Accepts an iterable of dict-like objects with a `text` key.
    """
    parts: List[str] = []
    for seg in segments:
        txt = seg.get("text") if isinstance(seg, dict) else getattr(seg, "text", None)
        if txt:
            parts.append(clean_text(txt))
    return separator.join(parts)
