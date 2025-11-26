"""
Utility helpers for search normalization and phrase detection.
"""
import re


def normalize_query(query: str) -> str:
    """Normalize search query for better matching."""
    normalized = re.sub(r"[^\w\s]", " ", query.lower()).strip()
    normalized = " ".join(normalized.split())
    return normalized


def is_phrase_query(query: str) -> bool:
    """Detect if query should use phrase matching (2-4 words)."""
    normalized = normalize_query(query)
    word_count = len(normalized.split())
    return 2 <= word_count <= 4


def calculate_phrase_boost(text: str, phrase: str) -> float:
    """Calculate boost factor for exact phrase matches."""
    text_normalized = normalize_query(text)
    phrase_normalized = normalize_query(phrase)

    if phrase_normalized in text_normalized:
        quote_length = len(text.split())
        if quote_length <= 5:
            return 10.0
        if quote_length <= 10:
            return 5.0
        return 2.0

    words = phrase_normalized.split()
    if len(words) >= 2:
        text_words = text_normalized.split()
        positions = []
        for word in words:
            try:
                pos = text_words.index(word)
                positions.append(pos)
            except ValueError:
                return 1.0

        if len(positions) == len(words):
            positions_sorted = sorted(positions)
            if positions_sorted == positions:
                max_gap = max(
                    positions[i + 1] - positions[i] for i in range(len(positions) - 1)
                )
                if max_gap == 1:
                    return 3.0
                if max_gap <= 3:
                    return 1.5

    return 1.0


__all__ = ["normalize_query", "is_phrase_query", "calculate_phrase_boost"]

