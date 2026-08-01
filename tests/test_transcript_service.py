from backend.schemas.video import TranscriptSegment, VideoMetadata
from backend.services.transcript_service import TranscriptService
from youtube_transcript_api import NoTranscriptFound


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


def test_transcript_service_whisper_fallback(monkeypatch):
    class DummyYT:
        @staticmethod
        def get_transcript(video_id):
            raise NoTranscriptFound(video_id, ["en"], None)

    # patch the YouTubeTranscriptApi used inside the module
    monkeypatch.setattr('backend.services.transcript_service.YouTubeTranscriptApi', DummyYT)
    called = {}

    def fake_whisper(self, url, video_id):
        called['was_called'] = True
        return type(
            'FakeTranscript',
            (),
            {
                'metadata': VideoMetadata(video_id=video_id, title=video_id),
                'segments': [TranscriptSegment(text='test', start=0.0, duration=1.0)],
                'full_text': 'test',
            },
        )()

    monkeypatch.setattr('backend.services.transcript_service.TranscriptService._whisper_fallback', fake_whisper)

    svc = TranscriptService()
    vt = svc.extract_transcript_from_youtube("dummyid")

    assert called['was_called'] is True
    assert vt.metadata.video_id == "dummyid"
    assert vt.full_text == 'test'
    assert len(vt.segments) == 1


def test_transcript_service_prefer_hindi_transcript(monkeypatch):
    class DummyTranscript:
        def __init__(self, language_code, name=""):
            self.language_code = language_code
            self.name = name
            self.is_generated = False
            self.is_translatable = False

        def fetch(self):
            return [{"text": f"text_{self.language_code}", "start": 0, "duration": 1}]

    class DummyYT:
        @staticmethod
        def get_transcript(video_id):
            raise NoTranscriptFound(video_id, ["en"], None)

        @staticmethod
        def list_transcripts(video_id):
            return [
                DummyTranscript("en"),
                DummyTranscript("hi"),
            ]

    monkeypatch.setattr('backend.services.transcript_service.YouTubeTranscriptApi', DummyYT)

    svc = TranscriptService()
    vt = svc.extract_transcript_from_youtube("dummyid")

    assert vt.full_text == 'text_hi'
    assert len(vt.segments) == 1


def test_transcript_service_prefers_hindi_over_get_transcript(monkeypatch):
    class DummyTranscript:
        def __init__(self, language_code, name=""):
            self.language_code = language_code
            self.name = name
            self.is_generated = False
            self.is_translatable = False

        def fetch(self):
            return [{"text": f"text_{self.language_code}", "start": 0, "duration": 1}]

    class DummyYT:
        @staticmethod
        def get_transcript(video_id):
            return [{"text": "text_en_default", "start": 0, "duration": 1}]

        @staticmethod
        def list_transcripts(video_id):
            return [
                DummyTranscript("en"),
                DummyTranscript("hi"),
            ]

    monkeypatch.setattr('backend.services.transcript_service.YouTubeTranscriptApi', DummyYT)

    svc = TranscriptService()
    vt = svc.extract_transcript_from_youtube("dummyid")

    assert vt.full_text == 'text_hi'
    assert len(vt.segments) == 1
