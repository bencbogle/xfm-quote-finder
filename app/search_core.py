"""
PostgreSQL-based search with full-text search optimization.
Optimized for production with proper indexing and query performance.
"""
import os
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

def search_quotes(query: str, top_k: int = 10, speaker_filter: str = None) -> List[Dict[str, Any]]:
    """
    Search quotes using database-specific full-text search.
    Supports both PostgreSQL and SQLite with optimized queries.
    """
    normalized_query = normalize_query(query)
    is_postgres = "postgresql" in os.getenv("DATABASE_URL", "").lower()
    
    with get_connection() as conn:
        if is_postgres:
            # PostgreSQL full-text search
            sql_query = """
                SELECT 
                    id, episode_id, timestamp_sec, speaker, text,
                    episode_name, spotify_url,
                    ts_rank(to_tsvector('english', text), plainto_tsquery('english', :query)) as rank
                FROM quotes
                WHERE to_tsvector('english', text) @@ plainto_tsquery('english', :query)
            """
            params = {"query": normalized_query}
            
            if speaker_filter:
                sql_query += " AND speaker = :speaker"
                params["speaker"] = speaker_filter.lower()
            
            sql_query += " ORDER BY rank DESC, timestamp_sec ASC LIMIT :limit"
            params["limit"] = top_k
            
        else:
            # SQLite FTS5 search
            sql_query = """
                SELECT 
                    q.id, q.episode_id, q.timestamp_sec, q.speaker, q.text,
                    q.episode_name, q.spotify_url,
                    bm25(quotes_fts) as rank
                FROM quotes_fts
                JOIN quotes q ON q.id = quotes_fts.rowid
                WHERE quotes_fts MATCH :query
            """
            params = {"query": normalized_query}
            
            if speaker_filter:
                sql_query += " AND q.speaker = :speaker"
                params["speaker"] = speaker_filter.lower()
            
            sql_query += " ORDER BY rank ASC LIMIT :limit"
            params["limit"] = top_k
        
        # Execute query
        result = conn.execute(text(sql_query), params)
        rows = result.fetchall()
        
        # Convert to results format
        results = []
        for row in rows:
            results.append({
                "episode_id": row.episode_id,
                "episode_name": row.episode_name or "",
                "timestamp_sec": row.timestamp_sec,
                "timestamp_hms": fmt_time(row.timestamp_sec),
                "speaker": row.speaker,
                "text": row.text,
                "spotify_url": row.spotify_url or "",
                "rank": float(row.rank) if row.rank else 0.0,
            })
        
        return results

def log_search(query: str, top_k: int, ip: str, user_agent: str):
    """Log search queries for analytics."""
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO search_log (ts, query, topk, ip, user_agent)
                VALUES (EXTRACT(EPOCH FROM NOW())::INTEGER, %s, %s, %s, %s)
            """, (query, top_k, ip, user_agent))
    except Exception as e:
        # Don't fail the search if logging fails
        print(f"Failed to log search: {e}")

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