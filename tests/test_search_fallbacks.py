from contextlib import contextmanager

from app import search_core
from app.spellcheck import SpellSuggestion


@contextmanager
def _dummy_connection():
    yield object()


def _patch_connection(monkeypatch):
    monkeypatch.setattr(search_core, "get_connection", _dummy_connection)


def test_search_quotes_exact_path(monkeypatch):
    _patch_connection(monkeypatch)

    expected_result = [{
        "episode_id": "xfm-s1e1",
        "episode_name": "Pilot",
        "timestamp_sec": 100,
        "timestamp_hms": "00:01:40",
        "speaker": "karl",
        "text": "Try both.",
        "spotify_url": "",
        "rank": 999.0,
    }]

    def fake_exact(conn, query, top_k, speaker_filter):
        return expected_result.copy()

    monkeypatch.setattr(search_core, "_run_exact_search", fake_exact)
    monkeypatch.setattr(search_core, "_run_fuzzy_fallback", lambda *args, **kwargs: None)
    monkeypatch.setattr(search_core, "_build_suggestion_payload", lambda *args, **kwargs: None)

    payload = search_core.search_quotes("Try both.", top_k=5)

    assert payload["search_type"] == "exact"
    assert payload["results"] == expected_result


def test_search_quotes_uses_fuzzy_fallback(monkeypatch):
    _patch_connection(monkeypatch)

    def fake_exact(conn, query, top_k, speaker_filter):
        if query == "whacking":
            return [{
                "episode_id": "xfm-s1e2",
                "episode_name": "Episode 2",
                "timestamp_sec": 200,
                "timestamp_hms": "00:03:20",
                "speaker": "karl",
                "text": "Keep whacking the cooker.",
                "spotify_url": "",
                "rank": 101.0,
            }]
        return []

    suggestion = SpellSuggestion(
        term="whacking",
        distance=1,
        frequency=10,
        confidence=0.9,
    )

    monkeypatch.setattr(search_core, "_run_exact_search", fake_exact)
    monkeypatch.setattr(
        search_core,
        "get_suggestions",
        lambda query, max_distance=2, max_suggestions=3: [suggestion],
    )

    payload = search_core.search_quotes("whaking", top_k=5)

    assert payload["search_type"] == "fuzzy"
    assert payload["query_used"] == "whacking"
    assert payload["results"]
    assert payload["auto_corrected"] is True


def test_search_quotes_returns_suggestion_when_no_fuzzy(monkeypatch):
    _patch_connection(monkeypatch)

    def fake_exact(conn, query, top_k, speaker_filter):
        if query == "whacking":
            return [{
                "episode_id": "xfm-s1e2",
                "episode_name": "Episode 2",
                "timestamp_sec": 210,
                "timestamp_hms": "00:03:30",
                "speaker": "karl",
                "text": "Keep whacking the cooker.",
                "spotify_url": "",
                "rank": 88.0,
            }]
        return []

    low_confidence = SpellSuggestion(
        term="whacking",
        distance=1,
        frequency=4,
        confidence=0.6,
    )

    monkeypatch.setattr(search_core, "_run_exact_search", fake_exact)
    monkeypatch.setattr(
        search_core,
        "get_suggestions",
        lambda query, max_distance=2, max_suggestions=3: [low_confidence],
    )

    payload = search_core.search_quotes("whaking", top_k=5)

    assert payload["search_type"] == "suggestion"
    assert payload["suggested_query"] == "whacking"
    assert payload["suggested_results"]

