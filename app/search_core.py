# SQLite-based search with FTS5 full-text search
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path("out/quotes.db")

def fmt_time(sec: int) -> str:
    """Format seconds as HH:MM:SS."""
    h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def search_quotes(query: str, top_k: int = 10, min_score: int = 85, speaker_filter: str = None):
    """Search quotes using SQLite FTS5 full-text search."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}. Run scripts/csv_to_sqlite.py first.")
    
    # Normalize query: remove punctuation and normalize whitespace
    import re
    normalized_query = re.sub(r'[^\w\s]', ' ', query.lower()).strip()
    normalized_query = ' '.join(normalized_query.split())  # Remove extra spaces
    
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    # Build the query with speaker filter
    sql_query = """
        SELECT q.id, q.episode_id, q.timestamp_sec, q.speaker, q.text,
               q.episode_name, q.spotify_url,
               bm25(quotes_fts) AS rank
        FROM quotes_fts
        JOIN quotes q ON q.id = quotes_fts.rowid
        WHERE quotes_fts MATCH ?
    """
    params = [normalized_query]
    
    if speaker_filter:
        sql_query += " AND q.speaker = ?"
        params.append(speaker_filter.lower())
    
    sql_query += """
        ORDER BY rank ASC
        LIMIT ?
    """
    params.append(top_k * 2)  # Get more results for filtering
    
    # Execute search
    cur.execute(sql_query, params)
    rows = cur.fetchall()
    con.close()

    # Convert to results format
    results = []
    for r in rows:
        # Convert FTS rank to score (0-100 scale, higher is better)
        # FTS rank is lower = better, so invert it
        rank = r["rank"] or 0
        score = max(85, int(100 - min(100, rank * 2)))  # Scale rank to 85-100 range
        
        # Remove score filtering since we're not showing scores anymore
        results.append({
            "episode_id": r["episode_id"],
            "episode_name": r["episode_name"],
            "timestamp_sec": r["timestamp_sec"],
            "timestamp_hms": fmt_time(r["timestamp_sec"]),
            "speaker": r["speaker"],
            "text": r["text"],
            "spotify_url": r["spotify_url"] or "",
            "rank": rank,  # Keep rank for sorting
        })
    
    # Sort by FTS rank (ascending) and then by timestamp
    # Lower rank = better match, so we sort by rank first
    results.sort(key=lambda x: (x.get("rank", 0), x["timestamp_sec"]))
    
    return results[:top_k]
