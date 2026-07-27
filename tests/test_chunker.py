from backend.schemas.video import VideoTranscript, VideoMetadata, TranscriptSegment
from backend.rag.chunker import chunk_transcript


def test_chunk_transcript_basic():
    segments = [
        TranscriptSegment(text="This is the first segment.", start=0.0, duration=5.0),
        TranscriptSegment(text="Second segment has more words to expand the length.", start=5.0, duration=6.0),
        TranscriptSegment(text="Third segment ends here.", start=11.0, duration=4.0),
    ]
    full_text = " \n".join([s.text for s in segments])
    metadata = VideoMetadata(video_id="vid123", title="Test Video", channel="Tester")
    vt = VideoTranscript(metadata=metadata, segments=segments, full_text=full_text)

    chunks = chunk_transcript(vt, chunk_size=40, chunk_overlap=10)
    assert isinstance(chunks, list)
    assert len(chunks) >= 1
    for i, c in enumerate(chunks, start=1):
        meta = c.get("metadata", {})
        assert meta.get("video_id") == "vid123"
        assert meta.get("chunk_number") == i
        assert "start_timestamp" in meta and "end_timestamp" in meta
