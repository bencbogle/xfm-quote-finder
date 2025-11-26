"""
Enhanced tests for fuzzy fallback functionality, including distance=2 fallback.
"""
from contextlib import contextmanager

from app import search_core
from app.spellcheck import SpellSuggestion


@contextmanager
def _dummy_connection():
    yield object()


def _patch_connection(monkeypatch):
    monkeypatch.setattr(search_core, "get_connection", _dummy_connection)


def test_fuzzy_fallback_tries_distance_2_when_distance_1_fails(monkeypatch):
    """Test that distance=2 suggestions are tried when distance=1 yields no results."""
    _patch_connection(monkeypatch)
    
    def fake_exact(conn, query, top_k, speaker_filter):
        # Only "monkey" (distance=2) yields results
        if query == "monkey":
            return [{
                "episode_id": "xfm-s1e3",
                "episode_name": "Episode 3",
                "timestamp_sec": 300,
                "timestamp_hms": "00:05:00",
                "speaker": "karl",
                "text": "Little monkey fella.",
                "spotify_url": "",
                "rank": 101.0,
            }]
        return []  # "money" (distance=1) yields no results
    
    # First suggestion is distance=1 but yields no results
    # Second suggestion is distance=2 and yields results
    suggestions = [
        SpellSuggestion(term="money", distance=1, frequency=20, confidence=0.88),
        SpellSuggestion(term="monkey", distance=2, frequency=15, confidence=0.82),
    ]
    
    monkeypatch.setattr(search_core, "_run_exact_search", fake_exact)
    monkeypatch.setattr(
        search_core,
        "get_suggestions",
        lambda query, max_distance=2, max_suggestions=3: suggestions,
    )
    
    payload = search_core.search_quotes("monky", top_k=5)
    
    # Should use distance=2 suggestion since distance=1 yielded no results
    assert payload["search_type"] == "fuzzy"
    assert payload["query_used"] == "monkey"
    assert payload["auto_corrected"] is True
    assert payload["results"]


def test_fuzzy_fallback_skips_low_confidence_distance_2(monkeypatch):
    """Test that low-confidence distance=2 suggestions are skipped."""
    _patch_connection(monkeypatch)
    
    def fake_exact(conn, query, top_k, speaker_filter):
        return []
    
    # Low confidence distance=2 suggestion
    suggestions = [
        SpellSuggestion(term="pilot", distance=1, frequency=12, confidence=0.85),
        SpellSuggestion(term="pilkington", distance=2, frequency=8, confidence=0.65),  # Below 0.8 threshold
    ]
    
    monkeypatch.setattr(search_core, "_run_exact_search", fake_exact)
    monkeypatch.setattr(
        search_core,
        "get_suggestions",
        lambda query, max_distance=2, max_suggestions=3: suggestions,
    )
    
    payload = search_core.search_quotes("pilkingtun", top_k=5)
    
    # Should fall through to suggestion prompt, not use low-confidence distance=2
    assert payload["search_type"] in ["suggestion", "none"]


def test_fuzzy_fallback_tries_multiple_distance_1_suggestions(monkeypatch):
    """Test that multiple distance=1 suggestions are tried in order."""
    _patch_connection(monkeypatch)
    
    call_order = []
    
    def fake_exact(conn, query, top_k, speaker_filter):
        call_order.append(query)
        # First suggestion yields no results, second yields results
        if query == "bat":
            return [{
                "episode_id": "xfm-s1e4",
                "episode_name": "Episode 4",
                "timestamp_sec": 400,
                "timestamp_hms": "00:06:40",
                "speaker": "karl",
                "text": "Like a bat.",
                "spotify_url": "",
                "rank": 101.0,
            }]
        return []
    
    # Multiple distance=1 suggestions (both pass auto-accept: Levenshtein <= 1, confidence >= 0.75)
    # "cat" -> "bat": distance 1 (c->b)
    # "cat" -> "car": distance 1 (t->r)
    suggestions = [
        SpellSuggestion(term="car", distance=1, frequency=18, confidence=0.87),
        SpellSuggestion(term="bat", distance=1, frequency=12, confidence=0.85),
    ]
    
    monkeypatch.setattr(search_core, "_run_exact_search", fake_exact)
    monkeypatch.setattr(
        search_core,
        "get_suggestions",
        lambda query, max_distance=1, max_suggestions=3: suggestions,
    )
    
    payload = search_core.search_quotes("cat", top_k=5)
    
    # Should try "car" first, then "bat"
    assert "car" in call_order
    assert payload["search_type"] == "fuzzy"
    assert payload["query_used"] == "bat"  # Second suggestion that worked


def test_fuzzy_fallback_respects_auto_accept_threshold(monkeypatch):
    """Test that _should_auto_accept threshold is respected."""
    _patch_connection(monkeypatch)
    
    def fake_exact(conn, query, top_k, speaker_filter):
        if query == "merchant":
            return [{"episode_id": "xfm-s1e5", "episode_name": "Episode 5", 
                    "timestamp_sec": 500, "timestamp_hms": "00:08:20",
                    "speaker": "steve", "text": "Stephen Merchant.", "spotify_url": "", "rank": 101.0}]
        return []
    
    # Low confidence suggestion (below 0.75 threshold)
    low_confidence = SpellSuggestion(
        term="merchant",
        distance=1,
        frequency=3,
        confidence=0.65,  # Below 0.75 threshold
    )
    
    monkeypatch.setattr(search_core, "_run_exact_search", fake_exact)
    monkeypatch.setattr(
        search_core,
        "get_suggestions",
        lambda query, max_distance=1, max_suggestions=3: [low_confidence],
    )
    
    payload = search_core.search_quotes("merchent", top_k=5)
    
    # Should not auto-accept low confidence, should go to suggestion prompt
    assert payload["search_type"] == "suggestion"


def test_fuzzy_fallback_handles_no_suggestions(monkeypatch):
    """Test that empty suggestions list is handled gracefully."""
    _patch_connection(monkeypatch)
    
    def fake_exact(conn, query, top_k, speaker_filter):
        return []
    
    monkeypatch.setattr(search_core, "_run_exact_search", fake_exact)
    monkeypatch.setattr(
        search_core,
        "get_suggestions",
        lambda query, max_distance=2, max_suggestions=3: [],
    )
    
    payload = search_core.search_quotes("xyzabc123", top_k=5)
    
    # Should fall through to suggestion prompt or none
    assert payload["search_type"] in ["suggestion", "none"]
    assert len(payload["results"]) == 0

