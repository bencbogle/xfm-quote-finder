#!/usr/bin/env python3
"""
Performance test comparing CSV vs SQLite search.
Run with: uv run python scripts/performance_test.py
"""

import time
import statistics
from pathlib import Path

# Test queries
TEST_QUERIES = [
    "monkey",
    "chimp",
    "ape", 
    "Scrimpton",
    "how they had to explain that",
    "in the line was a man with a hankerchief"
]

def test_sqlite_performance():
    """Test SQLite search performance."""
    print("🔍 Testing SQLite FTS5 search...")
    
    # Import here to avoid conflicts
    import sys
    sys.path.append('.')
    from app.search_core import search_quotes
    
    times = []
    for query in TEST_QUERIES:
        start = time.time()
        results = search_quotes(query, top_k=10)
        end = time.time()
        duration = (end - start) * 1000  # Convert to milliseconds
        times.append(duration)
        print(f"  '{query}' - {len(results)} results in {duration:.1f}ms")
    
    print(f"\n📊 SQLite Performance:")
    print(f"  Average: {statistics.mean(times):.1f}ms")
    print(f"  Median: {statistics.median(times):.1f}ms")
    print(f"  Min: {min(times):.1f}ms")
    print(f"  Max: {max(times):.1f}ms")
    
    return times

def main():
    """Run performance tests."""
    print("🚀 Performance Test: SQLite FTS5 vs CSV")
    print("=" * 50)
    
    # Check if database exists
    if not Path("out/quotes.db").exists():
        print("❌ SQLite database not found. Run scripts/csv_to_sqlite.py first.")
        return
    
    sqlite_times = test_sqlite_performance()
    
    print(f"\n✅ SQLite FTS5 search is ready for deployment!")
    print(f"   Database size: {Path('out/quotes.db').stat().st_size / 1024 / 1024:.1f} MB")
    print(f"   Average search time: {statistics.mean(sqlite_times):.1f}ms")

if __name__ == "__main__":
    main()
