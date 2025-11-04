"""
PostgreSQL-based search with full-text search optimization.
Optimized for production with proper indexing and query performance.
"""
import re
from typing import List, Dict, Any
from sqlalchemy import text
from app.database import get_connection

def fmt_time(sec: int) -> str:
    """Format seconds as HH:MM:SS."""
    h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def normalize_query(query: str) -> str:
    """Normalize search query for better matching."""
    # Remove punctuation and normalize whitespace
    normalized = re.sub(r'[^\w\s]', ' ', query.lower()).strip()
    normalized = ' '.join(normalized.split())  # Remove extra spaces
    return normalized

def is_phrase_query(query: str) -> bool:
    """Detect if query should use phrase matching (2-4 words)."""
    normalized = normalize_query(query)
    word_count = len(normalized.split())
    return 2 <= word_count <= 4

def calculate_phrase_boost(text: str, phrase: str) -> float:
    """Calculate boost factor for exact phrase matches."""
    # Normalize both for comparison (remove punctuation, lowercase)
    text_normalized = normalize_query(text)
    phrase_normalized = normalize_query(phrase)
    
    # Check for exact phrase match (normalized, case-insensitive)
    if phrase_normalized in text_normalized:
        # Higher boost for shorter quotes with exact phrase
        quote_length = len(text.split())
        if quote_length <= 5:
            return 10.0  # Very high boost for short exact matches
        elif quote_length <= 10:
            return 5.0   # High boost for medium exact matches
        else:
            return 2.0   # Moderate boost for longer exact matches
    
    # Check if words appear in order (proximity boost)
    words = phrase_normalized.split()
    if len(words) >= 2:
        # Find positions of words in normalized text
        text_words = text_normalized.split()
        positions = []
        for word in words:
            try:
                pos = text_words.index(word)
                positions.append(pos)
            except ValueError:
                return 1.0  # Word not found, no boost
        
        # Check if words are adjacent or close
        if len(positions) == len(words):
            positions_sorted = sorted(positions)
            # Check if words are in order
            if positions_sorted == positions:
                # Calculate proximity
                max_gap = max(positions[i+1] - positions[i] for i in range(len(positions)-1))
                if max_gap == 1:
                    return 3.0  # Adjacent words
                elif max_gap <= 3:
                    return 1.5  # Close words
    
    return 1.0  # No boost

def search_quotes(query: str, top_k: int = 10, speaker_filter: str = None) -> List[Dict[str, Any]]:
    """
    Search quotes using PostgreSQL full-text search with phrase matching.
    Uses phrase matching for better exact match results.
    """
    normalized_query = normalize_query(query)
    use_phrase = is_phrase_query(query)
    
    
    with get_connection() as conn:
        # PostgreSQL full-text search with exact match prioritization
        if use_phrase:
            # Single FTS query (fast, uses GIN index)
            # Exact match detection happens in Python after fetching
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
            
            # Also check for exact match separately (optimized: only check short quotes)
            # This is much faster than UNION with regex
            exact_match_query = """
                SELECT 
                    id, episode_id, timestamp_sec, speaker, text,
                    episode_name, spotify_url
                FROM quotes
                WHERE TRIM(REGEXP_REPLACE(REGEXP_REPLACE(LOWER(text), '[^a-z0-9 ]', ' ', 'g'), '\s+', ' ', 'g')) = :normalized_query_text
                AND LENGTH(text) < 100
            """
            if speaker_filter:
                exact_match_query += " AND speaker = :speaker"
            exact_match_query += " LIMIT 1"
        else:
            # Single word or many words - use standard word matching
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
        
        params = {"query": normalized_query}
        
        if speaker_filter:
            params["speaker"] = speaker_filter.lower()
            sql_query += " AND speaker = :speaker"
        
        sql_query += " ORDER BY phrase_rank DESC, word_rank DESC, timestamp_sec ASC LIMIT :limit"
        params["limit"] = top_k * 2  # Get more results to apply boost, then trim
        
        # Check for exact match separately (only for phrase queries)
        exact_match_row = None
        if use_phrase:
            exact_params = {"normalized_query_text": normalized_query}
            if speaker_filter:
                exact_params["speaker"] = speaker_filter.lower()
            try:
                exact_result = conn.execute(text(exact_match_query), exact_params)
                exact_match_row = exact_result.fetchone()
            except:
                pass  # If exact match query fails, continue with FTS results
        
        # Execute query
        result = conn.execute(text(sql_query), params)
        rows = result.fetchall()
        
        # Normalize query once for comparison
        query_normalized = normalize_query(query)
        
        # If we found an exact match separately, check if it's already in FTS results
        exact_match_id = None
        if exact_match_row:
            exact_match_id = exact_match_row.id
            # Check if it's already in FTS results
            found_in_fts = any(row.id == exact_match_id for row in rows)
            if not found_in_fts:
                # Add it to the beginning of rows with high rank
                from types import SimpleNamespace
                exact_row = SimpleNamespace(
                    id=exact_match_row.id,
                    episode_id=exact_match_row.episode_id,
                    timestamp_sec=exact_match_row.timestamp_sec,
                    speaker=exact_match_row.speaker,
                    text=exact_match_row.text,
                    episode_name=exact_match_row.episode_name,
                    spotify_url=exact_match_row.spotify_url,
                    phrase_rank=1000.0,
                    word_rank=1000.0
                )
                rows = [exact_row] + list(rows)
        
        # Convert to results format and apply phrase boost
        results = []
        
        for row in rows:
            # Get base rank (prefer phrase_rank if available, else word_rank)
            phrase_rank = getattr(row, 'phrase_rank', None)
            word_rank = getattr(row, 'word_rank', None)
            
            if use_phrase and phrase_rank is not None:
                base_rank = float(phrase_rank) if phrase_rank else 0.0
            elif word_rank is not None:
                base_rank = float(word_rank) if word_rank else 0.0
            else:
                base_rank = 0.0
            
            # Check for exact phrase match (normalized)
            text_normalized = normalize_query(row.text)
            is_exact_match = query_normalized == text_normalized
            
            # Calculate phrase boost
            phrase_boost = calculate_phrase_boost(row.text, query)
            
            # For exact matches, use a tiered ranking system to ensure they rank first
            if is_exact_match:
                quote_length = len(row.text.split())
                if quote_length <= 5:
                    final_rank = 1000.0 + (base_rank * phrase_boost)
                elif quote_length <= 15:
                    final_rank = 500.0 + (base_rank * phrase_boost)
                else:
                    final_rank = 100.0 + (base_rank * phrase_boost)
            else:
                # Non-exact matches use boosted base rank from PostgreSQL FTS
                final_rank = base_rank * phrase_boost
            
            results.append({
                "episode_id": row.episode_id,
                "episode_name": row.episode_name or "",
                "timestamp_sec": row.timestamp_sec,
                "timestamp_hms": fmt_time(row.timestamp_sec),
                "speaker": row.speaker,
                "text": row.text,
                "spotify_url": row.spotify_url or "",
                "rank": final_rank,
            })
        
        # Sort by rank (exact matches will be first due to high base scores)
        results.sort(key=lambda x: x['rank'], reverse=True)
        
        # Limit to top_k
        return results[:top_k]

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