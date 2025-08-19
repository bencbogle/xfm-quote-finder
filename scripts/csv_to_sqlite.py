import csv
import sqlite3
import time
from pathlib import Path

CSV = Path("out/quotes.csv")
DB = Path("out/quotes.db")

def main():
    """Convert CSV to SQLite with FTS5 full-text search index."""
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    cur = con.cursor()

    # Enable WAL mode for better performance
    cur.execute("PRAGMA journal_mode=WAL")
    
    # Create tables
    cur.executescript("""
    DROP TABLE IF EXISTS quotes;
    CREATE TABLE quotes(
      id INTEGER PRIMARY KEY,
      episode_id TEXT,
      timestamp_sec INTEGER,
      speaker TEXT,
      text TEXT,
      episode_name TEXT,
      spotify_url TEXT
    );

    DROP TABLE IF EXISTS quotes_fts;
    CREATE VIRTUAL TABLE quotes_fts USING fts5(
      text, content='quotes', content_rowid='id'
    );

    -- Search logging table
    CREATE TABLE IF NOT EXISTS search_log(
      id INTEGER PRIMARY KEY,
      ts INTEGER,              -- epoch seconds
      q TEXT,
      topk INTEGER,
      ip TEXT,
      user_agent TEXT
    );
    """)

    # Load CSV data
    print(f"Loading data from {CSV}...")
    with CSV.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append((
                row["episode_id"],
                int(row["timestamp_sec"]),
                row["speaker"],
                row["text"],
                row["episode_name"],
                row["spotify_url"]
            ))
    
    # Insert data
    print(f"Inserting {len(rows)} quotes...")
    cur.executemany(
        "INSERT INTO quotes(episode_id,timestamp_sec,speaker,text,episode_name,spotify_url) VALUES (?,?,?,?,?,?)",
        rows
    )
    
    # Populate FTS index
    print("Building FTS5 index...")
    cur.execute("INSERT INTO quotes_fts(rowid, text) SELECT id, text FROM quotes")

    con.commit()
    con.close()
    
    print(f"✅ Built {DB} with {len(rows)} quotes")
    print(f"📊 Database size: {DB.stat().st_size / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    main()
