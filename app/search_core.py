# Reusable fuzzy search logic (RapidFuzz) used by CLI and API.
import csv
from pathlib import Path
from rapidfuzz import process, fuzz
from typing import List, Dict, Any

CSV_PATH = Path("out/quotes.csv")

def load_rows() -> List[Dict[str, Any]]:
    """Load CSV rows into memory."""
    with CSV_PATH.open(encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = list(r)
    for row in rows:
        row["timestamp_sec"] = int(row["timestamp_sec"])
    return rows

def fmt_time(sec: int) -> str:
    """Format seconds as HH:MM:SS."""
    h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def search_quotes(query: str, top_k: int = 5, min_score: int = 80, speaker_filter: str = None):
    """Search quotes with fuzzy matching."""
    rows = load_rows()
    
    # Filter out very short quotes that cause false matches
    filtered_rows = []
    for r in rows:
        text = r["text"]
        # Skip quotes that are too short (likely false matches)
        if len(text.strip()) < 10:
            continue
        # Skip quotes that are just single words or very generic
        if len(text.split()) < 3:
            continue
        
        # Apply speaker filter if specified
        if speaker_filter and r["speaker"].lower() != speaker_filter.lower():
            continue
            
        filtered_rows.append(r)
    

    
    # Normalize query: lowercase + remove punctuation
    import re
    query_normalized = re.sub(r'[^\w\s]', ' ', query.lower()).strip()
    query_normalized = ' '.join(query_normalized.split())  # Remove extra spaces
    
    # Normalize texts for comparison
    texts_normalized = []
    for r in filtered_rows:
        text_normalized = re.sub(r'[^\w\s]', ' ', r["text"].lower()).strip()
        text_normalized = ' '.join(text_normalized.split())
        texts_normalized.append(text_normalized)
    
    # Use normalized text for search, but keep original for display
    matches = process.extract(
        query_normalized, texts_normalized, scorer=fuzz.WRatio, limit=top_k * 2
    )

    results = []
    for text, score, idx in matches:
        if score < min_score:
            continue
        r = filtered_rows[idx]
        results.append({
            "score": int(score),
            "episode_id": r["episode_id"],
            "episode_name": r["episode_name"],
            "timestamp_sec": r["timestamp_sec"],
            "timestamp_hms": fmt_time(r["timestamp_sec"]),
            "speaker": r["speaker"],
            "text": r["text"],
            "spotify_url": r.get("spotify_url") or "",
        })
    
    # Sort by score (descending) and then by timestamp to break ties
    results.sort(key=lambda x: (-x["score"], x["timestamp_sec"]))
    
    # Only return results that are close to the best score (within 2 points)
    if results:
        best_score = results[0]["score"]
        filtered_results = [r for r in results if r["score"] >= best_score - 2]
        return filtered_results[:top_k]
    
    return results[:top_k]
