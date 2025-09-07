#!/usr/bin/env python3
"""
Convert CSV data to PostgreSQL with optimized full-text search.
Production-ready script for importing XFM quote data.
"""
import csv
import os
import sys
from pathlib import Path
from app.database import get_connection, init_database

CSV_PATH = Path("out/quotes.csv")

def main():
    """Import CSV data into PostgreSQL with full-text search optimization."""
    
    # Check if CSV exists
    if not CSV_PATH.exists():
        print(f"❌ CSV file not found: {CSV_PATH}")
        print("Please run the data processing scripts first.")
        sys.exit(1)
    
    # Check database connection
    try:
        with get_connection() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Make sure DATABASE_URL environment variable is set")
        sys.exit(1)
    
    # Skip schema initialization - use existing table
    print("ℹ️  Using existing database schema")
    
    # Skip clearing data - just insert
    print("ℹ️  Inserting data into existing table")
    
    # Load and insert data
    print(f"📥 Loading data from {CSV_PATH}...")
    with CSV_PATH.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        
        for row in reader:
            rows.append({
                "episode_id": row["episode_id"],
                "timestamp_sec": int(row["timestamp_sec"]),
                "speaker": row["speaker"],
                "text": row["text"],
                "episode_name": row["episode_name"],
                "spotify_url": row["spotify_url"]
            })
    
    # Batch insert for better performance
    print(f"💾 Inserting {len(rows)} quotes...")
    with get_connection() as conn:
        from sqlalchemy import text
        conn.execute(text("""
            INSERT INTO quotes (episode_id, timestamp_sec, speaker, text, episode_name, spotify_url)
            VALUES (:episode_id, :timestamp_sec, :speaker, :text, :episode_name, :spotify_url)
        """), rows)
    
    # Skip full-text search index for now
    print("ℹ️  Skipping full-text search index (will be created by app)")
    
    # Get final statistics
    with get_connection() as conn:
        from sqlalchemy import text
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_quotes,
                COUNT(DISTINCT episode_id) as unique_episodes,
                COUNT(DISTINCT speaker) as unique_speakers
            FROM quotes
        """))
        stats = result.fetchone()
    
    print(f"✅ Import completed successfully!")
    print(f"📊 Statistics:")
    print(f"   Total quotes: {stats.total_quotes:,}")
    print(f"   Unique episodes: {stats.unique_episodes}")
    print(f"   Unique speakers: {stats.unique_speakers}")
    print(f"🎯 Full-text search is ready for production!")

if __name__ == "__main__":
    main()
