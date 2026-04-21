import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)

WORD_PATTERN = re.compile(r"\b[\w']+\b")


def normalize_text(raw_text: str) -> str:
    words = WORD_PATTERN.findall(raw_text.lower())
    result = " ".join(words)
    logger.debug("normalize_text: input_len=%d, output_len=%d, word_count=%d", len(raw_text), len(result), len(words))
    return result


def build_word_frequency(normalized_text: str) -> dict[str, int]:
    if not normalized_text:
        return {}

    counts = Counter(normalized_text.split())
    logger.debug("build_word_frequency: unique_words=%d, total_words=%d", len(counts), sum(counts.values()))
    return dict(counts)


def normalize_word(word: str) -> str:
    return " ".join(WORD_PATTERN.findall(word.lower()))
