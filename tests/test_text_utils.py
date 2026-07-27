from backend.utils.text import clean_text, join_segments


def test_clean_text_basic():
    assert clean_text("Hello   world\n") == "Hello world"
    assert clean_text("") == ""


def test_join_segments_defaults():
    segments = [{"text": "Hello"}, {"text": "  "}, {"text": "World"}]
    joined = join_segments(segments)
    assert "Hello" in joined
    assert "World" in joined
    # default separator is ' \n'
    assert " \n" in joined
