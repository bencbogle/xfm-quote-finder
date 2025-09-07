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
            conn.execute("SELECT 1")
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Make sure DATABASE_URL environment variable is set")
        sys.exit(1)
    
    # Initialize database schema
    print("🔧 Initializing database schema...")
    init_database()
    
    # Clear existing data
    print("🧹 Clearing existing data...")
    with get_connection() as conn:
        conn.execute("TRUNCATE TABLE quotes RESTART IDENTITY CASCADE")
    
    # Load and insert data
    print(f"📥 Loading data from {CSV_PATH}...")
    with CSV_PATH.open(encoding="utf-8") as f:
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
    
    # Batch insert for better performance
    print(f"💾 Inserting {len(rows)} quotes...")
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO quotes (episode_id, timestamp_sec, speaker, text, episode_name, spotify_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, rows)
    
    # Update full-text search index
    print("🔍 Updating full-text search index...")
    with get_connection() as conn:
        conn.execute("REINDEX INDEX idx_quotes_text_gin")
    
    # Get final statistics
    with get_connection() as conn:
        result = conn.execute("""
            SELECT 
                COUNT(*) as total_quotes,
                COUNT(DISTINCT episode_id) as unique_episodes,
                COUNT(DISTINCT speaker) as unique_speakers
            FROM quotes
        """)
        stats = result.fetchone()
    
    print(f"✅ Import completed successfully!")
    print(f"📊 Statistics:")
    print(f"   Total quotes: {stats.total_quotes:,}")
    print(f"   Unique episodes: {stats.unique_episodes}")
    print(f"   Unique speakers: {stats.unique_speakers}")
    print(f"🎯 Full-text search is ready for production!")

if __name__ == "__main__":
    main()
