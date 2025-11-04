#!/usr/bin/env python3
"""
Test the search API endpoint directly.
Useful for testing the full stack (API + search logic) before deploying.

Usage:
    # Start the server first: python -m uvicorn app.main:app --reload --port 8000
    # Then in another terminal:
    python scripts/test_api.py "Try both." karl
"""

import sys
import requests
from pathlib import Path

def test_api_search(query: str, speaker: str = None, top_k: int = 10, base_url: str = "http://localhost:8000"):
    """Test the search API endpoint."""
    params = {
        "q": query,
        "top_k": top_k,
        "test": "true"  # Skip logging for tests
    }
    
    if speaker:
        params["speaker"] = speaker
    
    try:
        response = requests.get(f"{base_url}/api/search", params=params)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"\n{'='*80}")
        print(f"API Test: '{query}'")
        if speaker:
            print(f"Speaker: {speaker}")
        print(f"{'='*80}\n")
        
        print(f"✅ API Response: {data['count']} result(s)\n")
        
        for i, r in enumerate(data['results'], 1):
            print(f"{i}. Rank: {r['rank']:.6f}")
            print(f"   Speaker: {r['speaker']}")
            print(f"   Episode: {r['episode_id']} — {r['episode_name']}")
            print(f"   Time: {r['timestamp_hms']}")
            print(f'   Text: "{r["text"]}"')
            if r.get("spotify_url"):
                print(f"   Spotify: {r['spotify_url']}")
            print()
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Could not connect to {base_url}")
        print("\nMake sure the server is running:")
        print("  python -m uvicorn app.main:app --reload --port 8000")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        if e.response:
            print(f"   Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/test_api.py 'query' [speaker] [base_url]")
        print("\nExample:")
        print("  python scripts/test_api.py 'Try both.' karl")
        print("  python scripts/test_api.py 'Try both.' karl http://localhost:8000")
        print("\nNote: Make sure the server is running first:")
        print("  python -m uvicorn app.main:app --reload --port 8000")
        sys.exit(1)
    
    query = sys.argv[1]
    speaker = sys.argv[2] if len(sys.argv) > 2 else None
    base_url = sys.argv[3] if len(sys.argv) > 3 else "http://localhost:8000"
    
    test_api_search(query, speaker, base_url=base_url)

