from app.services.text_processing import build_word_frequency, normalize_text, normalize_word


def test_normalize_text_and_frequency() -> None:
    raw = "Hello, world! Hello\nHELLO"
    normalized = normalize_text(raw)

    assert normalized == "hello world hello hello"
    assert build_word_frequency(normalized) == {"hello": 3, "world": 1}


def test_normalize_word() -> None:
    assert normalize_word("Hello!!!") == "hello"
    assert normalize_word("  multi word ") == "multi word"
