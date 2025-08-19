#!/usr/bin/env python3
"""
Simple analytics for search logs.
Run with: uv run python scripts/analytics.py
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path("out/quotes.db")

def main():
    """Show basic search analytics."""
    if not DB_PATH.exists():
        print("❌ Database not found. Run scripts/csv_to_sqlite.py first.")
        return
    
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    
    # Get total searches
    cur.execute("SELECT COUNT(*) FROM search_log")
    total_searches = cur.fetchone()[0]
    
    print(f"📊 Search Analytics")
    print(f"Total searches: {total_searches}")
    print()
    
    if total_searches == 0:
        print("No searches logged yet.")
        return
    
    # Top queries (last 7 days)
    week_ago = int((datetime.now() - timedelta(days=7)).timestamp())
    cur.execute("""
        SELECT q, COUNT(*) as c
        FROM search_log
        WHERE ts > ?
        GROUP BY q 
        ORDER BY c DESC 
        LIMIT 10
    """, (week_ago,))
    
    print("🔥 Top searches (last 7 days):")
    for row in cur.fetchall():
        print(f"  '{row[0]}' - {row[1]} searches")
    print()
    
    # Hourly volume (last 24 hours)
    day_ago = int((datetime.now() - timedelta(days=1)).timestamp())
    cur.execute("""
        SELECT strftime('%Y-%m-%d %H:00', ts, 'unixepoch') AS hour, COUNT(*)
        FROM search_log 
        WHERE ts > ?
        GROUP BY hour 
        ORDER BY hour DESC 
        LIMIT 24
    """, (day_ago,))
    
    print("📈 Hourly volume (last 24 hours):")
    for row in cur.fetchall():
        print(f"  {row[0]} - {row[1]} searches")
    
    con.close()

if __name__ == "__main__":
    main()
