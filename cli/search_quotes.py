# Terminal search tool for quick use.
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.search_core import search_quotes

def main():
    """Search quotes from command line and display formatted results."""
    if len(sys.argv) < 2:
        print("Usage: uv run python cli/search_quotes.py \"quote here\" [speaker]")
        print("Speakers: ricky, steve, karl")
        raise SystemExit(1)

    query = sys.argv[1]
    speaker_filter = sys.argv[2].lower() if len(sys.argv) > 2 else None
    
    # Validate speaker
    valid_speakers = ["ricky", "steve", "karl"]
    if speaker_filter and speaker_filter not in valid_speakers:
        print(f"Invalid speaker. Must be one of: {', '.join(valid_speakers)}")
        raise SystemExit(1)
    
    results = search_quotes(query, top_k=10, speaker_filter=speaker_filter)

    if not results:
        print("No matches found.")
        return

    print(f"\nTop matches for: \"{query}\"\n")
    for r in results:
        print(f"- [Rank: {r['rank']:.6f}] {r['speaker']} @ {r['timestamp_hms']} | {r['episode_id']} — {r['episode_name']}")
        print(f'  "{r["text"]}"')
        if r["spotify_url"]:
            print(f"  Spotify: {r['spotify_url']}")
        print()

if __name__ == "__main__":
    main()
