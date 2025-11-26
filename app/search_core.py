"""PostgreSQL-based search with full-text search optimization."""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, List, Literal, Optional, TypedDict

from rapidfuzz.distance import Levenshtein
from sqlalchemy import text

from app.database import get_connection
from app.spellcheck import SpellSuggestion, get_suggestions
from app.text_utils import calculate_phrase_boost, is_phrase_query, normalize_query

SearchType = Literal["exact", "fuzzy", "suggestion", "none"]


class SearchPayload(TypedDict, total=False):
    results: List[Dict[str, Any]]
    search_type: SearchType
    query_used: str
    original_query: str
    message: str
    suggested_query: str
    suggested_results: List[Dict[str, Any]]
    suggestion_confidence: float
    auto_corrected: bool

def fmt_time(sec: int) -> str:
    """Format seconds as HH:MM:SS."""
    h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def _run_exact_search(
    conn,
    query: str,
    top_k: int,
    speaker_filter: Optional[str],
) -> List[Dict[str, Any]]:
    normalized_query = normalize_query(query)
    use_phrase = is_phrase_query(query)

    if use_phrase:
        sql_query = """
            SELECT 
                id, episode_id, timestamp_sec, speaker, text,
                episode_name, spotify_url,
                ts_rank_cd(to_tsvector('english', text), 
                    phraseto_tsquery('english', :query), 32) as phrase_rank,
                ts_rank_cd(to_tsvector('english', text), 
                    plainto_tsquery('english', :query), 32) as word_rank
            FROM quotes
            WHERE (
                to_tsvector('english', text) @@ phraseto_tsquery('english', :query)
                OR to_tsvector('english', text) @@ plainto_tsquery('english', :query)
            )
        """

        exact_match_query = """
            SELECT 
                id, episode_id, timestamp_sec, speaker, text,
                episode_name, spotify_url
            FROM quotes
            WHERE TRIM(REGEXP_REPLACE(REGEXP_REPLACE(LOWER(text), '[^a-z0-9 ]', ' ', 'g'), '\\s+', ' ', 'g')) = :normalized_query_text
            AND LENGTH(text) < 100
        """
        if speaker_filter:
            exact_match_query += " AND speaker = :speaker"
        exact_match_query += " LIMIT 1"
    else:
        sql_query = """
            SELECT 
                id, episode_id, timestamp_sec, speaker, text,
                episode_name, spotify_url,
                0.0 as phrase_rank,
                ts_rank_cd(to_tsvector('english', text), 
                    plainto_tsquery('english', :query), 32) as word_rank
            FROM quotes
            WHERE to_tsvector('english', text) @@ plainto_tsquery('english', :query)
        """
        exact_match_query = None

    params: Dict[str, Any] = {"query": normalized_query, "limit": top_k * 2}
    if speaker_filter:
        params["speaker"] = speaker_filter.lower()
        sql_query += " AND speaker = :speaker"

    sql_query += " ORDER BY phrase_rank DESC, word_rank DESC, timestamp_sec ASC LIMIT :limit"

    rows = list(conn.execute(text(sql_query), params).fetchall())

    exact_match_row = None
    if use_phrase and exact_match_query:
        exact_params: Dict[str, Any] = {"normalized_query_text": normalized_query}
        if speaker_filter:
            exact_params["speaker"] = speaker_filter.lower()
        try:
            exact_result = conn.execute(text(exact_match_query), exact_params)
            exact_match_row = exact_result.fetchone()
        except Exception:
            exact_match_row = None

    if exact_match_row:
        exact_match_id = exact_match_row.id
        found_in_fts = any(row.id == exact_match_id for row in rows)
        if not found_in_fts:
            exact_row = SimpleNamespace(
                id=exact_match_row.id,
                episode_id=exact_match_row.episode_id,
                timestamp_sec=exact_match_row.timestamp_sec,
                speaker=exact_match_row.speaker,
                text=exact_match_row.text,
                episode_name=exact_match_row.episode_name,
                spotify_url=exact_match_row.spotify_url,
                phrase_rank=1000.0,
                word_rank=1000.0,
            )
            rows = [exact_row] + rows

    query_normalized = normalize_query(query)
    results: List[Dict[str, Any]] = []

    for row in rows:
        phrase_rank = getattr(row, "phrase_rank", None)
        word_rank = getattr(row, "word_rank", None)

        if use_phrase and phrase_rank is not None:
            base_rank = float(phrase_rank) if phrase_rank else 0.0
        elif word_rank is not None:
            base_rank = float(word_rank) if word_rank else 0.0
        else:
            base_rank = 0.0

        text_normalized = normalize_query(row.text)
        is_exact_match = query_normalized == text_normalized
        phrase_boost = calculate_phrase_boost(row.text, query)

        if is_exact_match:
            quote_length = len(row.text.split())
            if quote_length <= 5:
                final_rank = 1000.0 + (base_rank * phrase_boost)
            elif quote_length <= 15:
                final_rank = 500.0 + (base_rank * phrase_boost)
            else:
                final_rank = 100.0 + (base_rank * phrase_boost)
        else:
            final_rank = base_rank * phrase_boost

        results.append(
            {
                "episode_id": row.episode_id,
                "episode_name": row.episode_name or "",
                "timestamp_sec": row.timestamp_sec,
                "timestamp_hms": fmt_time(row.timestamp_sec),
                "speaker": row.speaker,
                "text": row.text,
                "spotify_url": row.spotify_url or "",
                "rank": final_rank,
            }
        )

    results.sort(key=lambda x: x["rank"], reverse=True)
    return results[:top_k]


def _should_auto_accept(query: str, suggestion: SpellSuggestion) -> bool:
    if suggestion.distance > 1:
        return False
    normalized_query = normalize_query(query)
    normalized_suggestion = normalize_query(suggestion.term)
    if normalized_query == normalized_suggestion:
        return False
    if Levenshtein.distance(normalized_query, normalized_suggestion) > 1:
        return False
    return suggestion.confidence >= 0.75


def _run_fuzzy_fallback(
    conn,
    query: str,
    top_k: int,
    speaker_filter: Optional[str],
) -> Optional[SearchPayload]:
    # Try distance=1 first (most confident)
    suggestions = get_suggestions(query, max_distance=1, max_suggestions=3)
    for suggestion in suggestions:
        if not _should_auto_accept(query, suggestion):
            continue
        results = _run_exact_search(conn, suggestion.term, top_k, speaker_filter)
        if results:
            return {
                "results": results,
                "search_type": "fuzzy",
                "query_used": suggestion.term,
                "original_query": query,
                "message": f"Showing approximate matches for '{suggestion.term}'",
                "auto_corrected": True,
                "suggestion_confidence": suggestion.confidence,
            }
    
    # If distance=1 didn't yield results, try distance=2 (but require higher confidence)
    suggestions = get_suggestions(query, max_distance=2, max_suggestions=3)
    for suggestion in suggestions:
        # Only accept distance=2 if distance=1 didn't work and confidence is high
        if suggestion.distance > 1 and suggestion.confidence >= 0.8:
            results = _run_exact_search(conn, suggestion.term, top_k, speaker_filter)
            if results:
                return {
                    "results": results,
                    "search_type": "fuzzy",
                    "query_used": suggestion.term,
                    "original_query": query,
                    "message": f"Showing approximate matches for '{suggestion.term}'",
                    "auto_corrected": True,
                    "suggestion_confidence": suggestion.confidence,
                }
    
    return None


def _build_suggestion_payload(
    conn,
    query: str,
    top_k: int,
    speaker_filter: Optional[str],
) -> Optional[SearchPayload]:
    suggestions = get_suggestions(query, max_distance=2, max_suggestions=3)
    for suggestion in suggestions:
        normalized_query = normalize_query(query)
        normalized_term = normalize_query(suggestion.term)
        if normalized_query == normalized_term:
            continue
        suggestion_results = _run_exact_search(conn, suggestion.term, top_k, speaker_filter)
        if suggestion_results:
            return {
                "results": [],
                "search_type": "suggestion",
                "query_used": query,
                "original_query": query,
                "message": f"Did you mean '{suggestion.term}'?",
                "suggested_query": suggestion.term,
                "suggested_results": suggestion_results,
                "suggestion_confidence": suggestion.confidence,
            }
    return None


def search_quotes(
    query: str,
    top_k: int = 10,
    speaker_filter: Optional[str] = None,
) -> SearchPayload:
    """
    Hybrid search flow:
        1. Exact PostgreSQL full-text search.
        2. Fuzzy fallback using SymSpell suggestions (edit distance <= 1).
        3. Spell suggestion prompt with preview results.
    """
    with get_connection() as conn:
        exact_results = _run_exact_search(conn, query, top_k, speaker_filter)
        if exact_results:
            return {
                "results": exact_results,
                "search_type": "exact",
                "query_used": query,
                "original_query": query,
            }

        fuzzy_payload = _run_fuzzy_fallback(conn, query, top_k, speaker_filter)
        if fuzzy_payload:
            return fuzzy_payload

        suggestion_payload = _build_suggestion_payload(conn, query, top_k, speaker_filter)
        if suggestion_payload:
            return suggestion_payload

    return {
        "results": [],
        "search_type": "none",
        "query_used": query,
        "original_query": query,
    }

def log_search(query: str, top_k: int, ip: str, user_agent: str):
    """Log search queries for analytics."""
    try:
        with get_connection() as conn:
            with conn.begin():
                conn.execute(text("""
                    INSERT INTO search_log (ts, query, topk, ip, user_agent)
                    VALUES (EXTRACT(EPOCH FROM NOW())::INTEGER, :query, :topk, :ip, :user_agent)
                """), {
                    "query": query,
                    "topk": top_k,
                    "ip": ip,
                    "user_agent": user_agent
                })
    except Exception as e:
        # Don't fail the search if logging fails
        print(f"Failed to log search: {e}")

def log_visit(ip: str, user_agent: str, path: str):
    """Log page visits for visitor tracking."""
    try:
        with get_connection() as conn:
            with conn.begin():
                conn.execute(text("""
                    INSERT INTO visitors (ip, user_agent, path)
                    VALUES (:ip, :user_agent, :path)
                """), {
                    "ip": ip,
                    "user_agent": user_agent,
                    "path": path
                })
    except Exception as e:
        # Don't fail if logging fails
        print(f"Failed to log visit: {e}")

def get_stats():
    """Get database statistics."""
    with get_connection() as conn:
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_quotes,
                COUNT(DISTINCT episode_id) as unique_episodes,
                ARRAY_AGG(DISTINCT episode_id ORDER BY episode_id) as episodes
            FROM quotes
        """))
        row = result.fetchone()
        return {
            "total_quotes": row.total_quotes,
            "unique_episodes": row.unique_episodes,
            "episodes": row.episodes
        }

def get_visitor_stats(days: int = None):
    """
    Get unique visitor statistics.
    
    Args:
        days: Number of days to look back (None for all time)
    
    Returns:
        Dictionary with visitor statistics
    """
    with get_connection() as conn:
        if days:
            result = conn.execute(text(f"""
                SELECT 
                    COUNT(DISTINCT ip) as unique_visitors,
                    COUNT(*) as total_visits,
                    MIN(visited_at) as first_visit,
                    MAX(visited_at) as last_visit
                FROM visitors
                WHERE visited_at >= NOW() - INTERVAL '{days} days'
            """))
        else:
            result = conn.execute(text("""
                SELECT 
                    COUNT(DISTINCT ip) as unique_visitors,
                    COUNT(*) as total_visits,
                    MIN(visited_at) as first_visit,
                    MAX(visited_at) as last_visit
                FROM visitors
            """))
        
        row = result.fetchone()
        
        # Get daily breakdown for last 30 days
        daily_result = conn.execute(text("""
            SELECT 
                DATE(visited_at) as visit_date,
                COUNT(DISTINCT ip) as unique_visitors,
                COUNT(*) as total_visits
            FROM visitors
            WHERE visited_at >= NOW() - INTERVAL '30 days'
            GROUP BY DATE(visited_at)
            ORDER BY visit_date DESC
            LIMIT 30
        """))
        daily_rows = daily_result.fetchall()
        
        return {
            "unique_visitors": row.unique_visitors or 0,
            "total_visits": row.total_visits or 0,
            "first_visit": str(row.first_visit) if row.first_visit else None,
            "last_visit": str(row.last_visit) if row.last_visit else None,
            "daily_breakdown": [
                {
                    "date": str(r.visit_date),
                    "unique_visitors": r.unique_visitors,
                    "total_visits": r.total_visits
                }
                for r in daily_rows
            ]
        }