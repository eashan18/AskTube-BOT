from backend.services.transcript_service import TranscriptService


def test_transcript_service_mock(monkeypatch):
    sample = [{"text": "Hello world", "start": 0, "duration": 2}, {"text": "More text here", "start": 2, "duration": 3}]

    class DummyYT:
        @staticmethod
        def get_transcript(video_id):
            return sample

    # patch the YouTubeTranscriptApi used inside the module
    monkeypatch.setattr('backend.services.transcript_service.YouTubeTranscriptApi', DummyYT)

    svc = TranscriptService()
    vt = svc.extract_transcript_from_youtube("dummyid")
    assert vt.metadata.video_id == "dummyid"
    assert "Hello world" in vt.full_text
    assert len(vt.segments) == 2
