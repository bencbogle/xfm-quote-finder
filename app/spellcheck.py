"""
Spell checking helpers backed by SymSpell.
"""
from __future__ import annotations

import re
import threading
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List

from symspellpy import SymSpell, Verbosity
from sqlalchemy import text

from app.database import get_connection
from app.text_utils import normalize_query


@dataclass(frozen=True)
class SpellSuggestion:
    term: str
    distance: int
    frequency: int
    confidence: float


_symspell: SymSpell | None = None
_symspell_lock = threading.Lock()


def _build_symspell() -> SymSpell:
    symspell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
    vocabulary = Counter()

    with get_connection() as conn:
        result = conn.execute(
            text(
                """
                SELECT text
                FROM quotes
                WHERE text IS NOT NULL
            """
            )
        )
        for row in result:
            for word in _iter_words(row.text):
                vocabulary[word] += 1

    for word, freq in vocabulary.items():
        symspell.create_dictionary_entry(word, freq)

    return symspell


def _iter_words(text: str) -> Iterable[str]:
    for word in re.findall(r"[a-z]+", text.lower()):
        if len(word) >= 2:
            yield word


def _get_symspell() -> SymSpell:
    global _symspell
    if _symspell is None:
        with _symspell_lock:
            if _symspell is None:
                _symspell = _build_symspell()
    return _symspell


def get_suggestions(query: str, max_distance: int = 2, max_suggestions: int = 3) -> List[SpellSuggestion]:
    symspell = _get_symspell()
    normalized_query = normalize_query(query)

    suggestions = symspell.lookup_compound(
        normalized_query,
        max_dictionary_edit_distance=max_distance,
    )

    if not suggestions:
        suggestions = symspell.lookup(
            normalized_query,
            Verbosity.CLOSEST,
            max_distance,
        )

    ranked: List[SpellSuggestion] = []
    query_length = max(len(normalized_query), 1)

    for suggestion in suggestions:
        term = suggestion.term.strip()
        if not term:
            continue
        confidence = max(0.0, 1.0 - suggestion.distance / query_length)
        ranked.append(
            SpellSuggestion(
                term=term,
                distance=suggestion.distance,
                frequency=suggestion.count,
                confidence=confidence,
            )
        )

    ranked.sort(
        key=lambda s: (
            s.distance,
            -s.frequency,
            -s.confidence,
        )
    )

    return ranked[:max_suggestions]

