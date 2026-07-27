"""Transcript chunking utilities using LangChain's text splitter.

Produces semantically-sized chunks and maps them to transcript timestamps
so each chunk metadata contains `start_timestamp` and `end_timestamp`.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Any

from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..config.settings import get_settings
from ..schemas.video import VideoTranscript


def chunk_transcript(video_transcript: VideoTranscript, chunk_size: int | None = None, chunk_overlap: int | None = None) -> List[Dict[str, Any]]:
    """Split a VideoTranscript into chunks and attach metadata for each chunk.

    Returns a list of dictionaries with keys: `content` and `metadata`.

    Metadata includes: Video ID, Video Title, Channel Name, Chunk Number,
    Start Timestamp, End Timestamp, Original Text, Upload Time.
    """
    settings = get_settings()
    chunk_size = int(chunk_size or settings.CHUNK_SIZE)
    chunk_overlap = int(chunk_overlap or settings.CHUNK_OVERLAP)

    # Build the canonical full text (should match how transcript was stored)
    full_text = video_transcript.full_text

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = splitter.split_text(full_text)

    # Build segment char ranges to map character index -> timestamp
    segment_ranges: List[dict] = []
    cursor = 0
    sep = " \n"
    for seg in video_transcript.segments:
        seg_text = seg.text.strip()
        if not seg_text:
            continue
        start_idx = cursor
        end_idx = start_idx + len(seg_text)
        segment_ranges.append({
            "start_idx": start_idx,
            "end_idx": end_idx,
            "start_time": seg.start,
            "end_time": seg.start + (seg.duration or 0.0),
        })
        # advance cursor plus separator
        cursor = end_idx + len(sep)

    results: List[Dict[str, Any]] = []
    search_pos = 0
    for i, chunk in enumerate(chunks, start=1):
        # find the chunk in the original full_text starting from last position
        start_idx = full_text.find(chunk, search_pos)
        if start_idx == -1:
            # fallback: try from beginning (should rarely happen)
            start_idx = full_text.find(chunk)
        end_idx = start_idx + len(chunk) if start_idx != -1 else len(full_text)

        # find corresponding timestamps
        start_time = None
        end_time = None
        for seg in segment_ranges:
            if start_time is None and seg["start_idx"] <= start_idx < seg["end_idx"]:
                start_time = seg["start_time"]
            if seg["start_idx"] < end_idx <= seg["end_idx"]:
                end_time = seg["end_time"]
            # if both found, break
            if start_time is not None and end_time is not None:
                break

        # if start_time or end_time not found, approximate using nearest segment
        if start_time is None and segment_ranges:
            # pick the first segment whose end_idx > start_idx else last segment
            for seg in segment_ranges:
                if seg["end_idx"] > start_idx:
                    start_time = seg["start_time"]
                    break
            else:
                start_time = segment_ranges[-1]["start_time"]

        if end_time is None and segment_ranges:
            for seg in segment_ranges:
                if seg["end_idx"] >= end_idx:
                    end_time = seg["end_time"]
                    break
            else:
                end_time = segment_ranges[-1]["end_time"]

        metadata = {
            "video_id": video_transcript.metadata.video_id,
            "video_title": video_transcript.metadata.title,
            "channel_name": video_transcript.metadata.channel,
            "chunk_number": i,
            "start_timestamp": float(start_time) if start_time is not None else 0.0,
            "end_timestamp": float(end_time) if end_time is not None else 0.0,
            "original_text": chunk,
            "upload_time": video_transcript.extracted_at.isoformat() if isinstance(video_transcript.extracted_at, datetime) else None,
        }

        results.append({"content": chunk, "metadata": metadata})

        # advance search position
        search_pos = end_idx

    return results
