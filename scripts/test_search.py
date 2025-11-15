#!/usr/bin/env python3
"""
Test script for search functionality.
Run this locally to test search changes before deploying.

Usage:
    python scripts/test_search.py "Try both." karl
    python scripts/test_search.py "try both" karl
    python scripts/test_search.py "knob at night" karl
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.search_core import search_quotes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_search(query: str, speaker: str = None, top_k: int = 10):
    """Test a search query and display results."""
    print(f"\n{'='*80}")
    print(f"Testing search: '{query}'")
    if speaker:
        print(f"Speaker filter: {speaker}")
    print(f"{'='*80}\n")
    
    try:
        from app.search_core import normalize_query
        query_normalized = normalize_query(query)
        
        payload = search_quotes(query, top_k=top_k, speaker_filter=speaker)
        results = payload.get("results", [])
        
        if not results:
            message = payload.get("message")
            if message:
                print(message)
            print("❌ No results found.")
            return
        
        print(f"✅ Found {len(results)} result(s)\n")
        
        # Display results with ranking info
        exact_match_found = False
        for i, r in enumerate(results, 1):
            text_normalized = normalize_query(r['text'])
            is_exact = query_normalized == text_normalized
            
            print(f"{i}. Rank: {r['rank']:.6f}")
            if is_exact:
                print("   ⭐⭐ EXACT MATCH ⭐⭐")
                exact_match_found = True
            print(f"   Speaker: {r['speaker']}")
            print(f"   Episode: {r['episode_id']} — {r['episode_name']}")
            print(f"   Time: {r['timestamp_hms']}")
            print(f'   Text: "{r["text"]}"')
            
            if r.get("spotify_url"):
                print(f"   Spotify: {r['spotify_url']}")
            print()
        
        # Check if first result is the expected exact match
        if results:
            first_text_normalized = normalize_query(results[0]['text'])
            if query_normalized == first_text_normalized:
                print("✅ Top result is an exact match!")
            else:
                print(f"⚠️  Top result is NOT an exact match")
                print(f"   Expected: '{query_normalized}'")
                print(f"   Got: '{first_text_normalized}'")
                if not exact_match_found:
                    print(f"   ⚠️  WARNING: No exact match found in any results!")
                    print(f"   This suggests the exact match isn't being returned by PostgreSQL.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def run_test_suite():
    """Run a suite of test searches to verify search improvements."""
    print("\n" + "="*80)
    print("RUNNING SEARCH TEST SUITE")
    print("="*80)
    
    tests = [
        ("Try both.", "karl", "Should find exact match 'Try both.' by Karl"),
        ("try both", "karl", "Should find exact match without punctuation"),
        ("Try both", "karl", "Should find exact match with different case"),
        ("knob at night", "karl", "Should find phrase match"),
        ("knob", "karl", "Single word search"),
    ]
    
    passed = 0
    failed = 0
    
    for query, speaker, description in tests:
        print(f"\n{'─'*80}")
        print(f"Test: {description}")
        print(f"{'─'*80}")
        try:
            payload = search_quotes(query, top_k=5, speaker_filter=speaker)
            results = payload.get("results", [])
            if results:
                print(f"✅ Passed: Found {len(results)} result(s)")
                print(f"   Top result: \"{results[0]['text'][:60]}...\"")
                passed += 1
            else:
                print(f"⚠️  No results found")
                failed += 1
        except Exception as e:
            print(f"❌ Failed: {e}")
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"Test Suite Results: {passed} passed, {failed} failed")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("\nTo test locally, you need:")
        print("1. A PostgreSQL database (local or Railway)")
        print("2. Set DATABASE_URL in .env file or environment")
        print("\nExample .env file:")
        print("  DATABASE_URL=postgresql://user:password@localhost:5432/xfm_quotes")
        print("\nOr use Railway's local development:")
        print("  railway link")
        print("  railway run python scripts/test_search.py 'Try both.' karl")
        sys.exit(1)
    
    if len(sys.argv) == 1:
        # Run test suite
        run_test_suite()
    elif len(sys.argv) == 2:
        # Single query, no speaker filter
        query = sys.argv[1]
        test_search(query)
    elif len(sys.argv) == 3:
        # Query with speaker filter
        query = sys.argv[1]
        speaker = sys.argv[2].lower()
        test_search(query, speaker=speaker)
    else:
        print("Usage:")
        print("  python scripts/test_search.py                    # Run test suite")
        print("  python scripts/test_search.py 'query'           # Search without filter")
        print("  python scripts/test_search.py 'query' speaker  # Search with speaker filter")
        sys.exit(1)

