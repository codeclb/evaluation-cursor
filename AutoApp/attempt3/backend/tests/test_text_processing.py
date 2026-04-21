from app.text_processing import build_word_frequency, normalize_text


def test_normalize_text_removes_punctuation_and_lowercases():
    raw = "Hello, HELLO!!! World\nworld"
    assert normalize_text(raw) == "hello hello world world"


def test_build_word_frequency_counts_words():
    freq = build_word_frequency("alpha beta beta")
    assert freq == {"alpha": 1, "beta": 2}
