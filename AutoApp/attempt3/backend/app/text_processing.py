import re
from collections import Counter


def normalize_text(raw_text: str) -> str:
    lowered = raw_text.lower()
    cleaned = re.sub(r"[^\w\s]", " ", lowered)
    normalized = re.sub(r"\s+", " ", cleaned).strip()
    return normalized


def build_word_frequency(normalized_text: str) -> dict[str, int]:
    if not normalized_text:
        return {}
    tokens = normalized_text.split(" ")
    return dict(Counter(tokens))
