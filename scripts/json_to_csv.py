# Convert all JSON transcripts in data/ → a single out/quotes.csv (one row per line), converting ns→sec and adding Spotify deep-links.
import json, csv
from pathlib import Path

DATA_DIR = Path("data")
OUT_DIR = Path("out")
OUT_FILE = OUT_DIR / "quotes.csv"

def ns_to_sec(ns): 
    """Convert nanoseconds to seconds."""
    try: return int(int(ns) / 1_000_000_000)
    except: return 0

def episode_id(meta: dict) -> str:
    """Generate episode ID from metadata in format 'pub-sXeY'."""
    pub = meta.get("publication", "pod")
    s = meta.get("series", "")
    e = meta.get("episode", "")
    return f"{pub}-s{s}e{e}".lower()

# Global cache for Spotify episode mappings
_SPOTIFY_MAPPING_CACHE = None

def load_episode_mapping():
    """Load the episode mapping from our generated mapping file."""
    mapping_file = Path("episode_mapping.json")
    if mapping_file.exists():
        import json
        with open(mapping_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def convert_episode_name_to_spotify_format(episode_id: str) -> str:
    """Convert our episode ID format to Spotify episode name format."""
    # Examples:
    # ep-podcast-S1E11.json -> TRGS Podcast S01E11
    # ep-xfm-S1E11.json -> S01E11 | Remastered  
    # ep-guide-S1E01.json -> TRGS Guide to... Medicine
    
    if episode_id.startswith("podcast-"):
        # podcast-s1e11 -> TRGS Podcast S01E11
        series_episode = episode_id.replace("podcast-", "").upper()
        # Add leading zeros: S1E11 -> S01E11
        if "S" in series_episode and "E" in series_episode:
            parts = series_episode.split("E")
            series = parts[0]  # S1
            episode = parts[1]  # 11
            series_num = series[1:]  # 1
            series_episode = f"S{series_num.zfill(2)}E{episode.zfill(2)}"  # S01E11
        
        # Special handling for Season 4 episodes with holiday names
        if series_episode == "S04E01":
            return "TRGS Podcast S04E01 Halloween"
        elif series_episode == "S04E02":
            return "TRGS Podcast S04E02 Thanksgiving"
        elif series_episode == "S04E03":
            return "TRGS Podcast S04E03 Christmas"
        
        # Special handling for Season 5 episodes (all map to single "TRGS Podcast Series 5" episode)
        if series_episode.startswith("S05"):
            return "TRGS Podcast Series 5"
        
        return f"TRGS Podcast {series_episode}"
    
    elif episode_id.startswith("xfm-"):
        # xfm-s1e11 -> S01E11 | Remastered
        series_episode = episode_id.replace("xfm-", "").upper()
        # Add leading zeros: S1E11 -> S01E11
        if "S" in series_episode and "E" in series_episode:
            parts = series_episode.split("E")
            series = parts[0]  # S1
            episode = parts[1]  # 11
            series_num = series[1:]  # 1
            series_episode = f"S{series_num.zfill(2)}E{episode.zfill(2)}"  # S01E11
        
        # Special handling for Season 0 episodes (no "Remastered" suffix)
        if series_episode.startswith("S00"):
            return series_episode
        
        # Special handling for Season 4 episodes (with "[NEW]" suffix)
        if series_episode.startswith("S04"):
            return f"{series_episode} | Remastered [NEW]"
        
        return f"{series_episode} | Remastered"
    
    elif episode_id.startswith("guide-"):
        # guide-s1e01 -> TRGS Guide to... Medicine
        # We need to map guide episodes by their specific names
        guide_mapping = {
            "guide-s1e01": "TRGS Guide to... Medicine",
            "guide-s1e02": "TRGS Guide to... Natural History", 
            "guide-s1e03": "TRGS Guide to... The Arts",
            "guide-s1e04": "TRGS Guide to... Philosophy",
            "guide-s1e05": "TRGS Guide to... Society",
            "guide-s2e01": "TRGS Guide to... The English",
            "guide-s2e02": "TRGS Guide to... The Future",
            "guide-s2e03": "TRGS Guide to... Law & Order",
            "guide-s2e04": "TRGS Guide to... The Earth",
            "guide-s2e05": "TRGS Guide to... The Human Body",
            "guide-s2e06": "TRGS Guide to... The World Cup",
            "guide-s2e07": "TRGS Guide to... Armed Forces",
        }
        return guide_mapping.get(episode_id, "")
    
    return ""

def get_spotify_episode_mapping():
    """Load mapping of episode names to Spotify episode IDs from our mapping file (cached)."""
    global _SPOTIFY_MAPPING_CACHE
    
    if _SPOTIFY_MAPPING_CACHE is not None:
        return _SPOTIFY_MAPPING_CACHE
    
    # Load from our generated mapping
    episode_mappings = load_episode_mapping()
    
    mappings = {}
    for mapping in episode_mappings:
        if mapping["mapped"]:
            episode_name = mapping["spotify_episode_name"]
            spotify_id = mapping["spotify_id"]
            mappings[episode_name] = spotify_id
    
    print(f"Loaded {len(mappings)} Spotify episode mappings")
    _SPOTIFY_MAPPING_CACHE = mappings
    return mappings

def spotify_url(metadata: dict | None, sec: int, episode_id: str = None) -> str:
    """Generate Spotify URL with timestamp from metadata."""
    if not metadata: return ""
    
    # For XFM episodes, try to find the correct remastered episode
    spotify_uri = metadata.get("spotify_uri", "")
    if spotify_uri and "episode:" in spotify_uri:
        # Try to map to the correct remastered episode
        if episode_id:
            spotify_episode_name = convert_episode_name_to_spotify_format(episode_id)
            if spotify_episode_name:
                mappings = get_spotify_episode_mapping()
                if spotify_episode_name in mappings:
                    episode_id = mappings[spotify_episode_name]
                    return f"https://open.spotify.com/episode/{episode_id}?t={sec}"
        
        # Fallback to a known working episode ID
        # TODO: Replace this with proper episode mapping
        working_episode_id = "6qYL2Hg6zHPyiYxbJIqRma"
        return f"https://open.spotify.com/episode/{working_episode_id}?t={sec}"
    
    # For guide episodes (which don't have spotify_uri), try to map by episode name
    if episode_id:
        spotify_episode_name = convert_episode_name_to_spotify_format(episode_id)
        if spotify_episode_name:
            mappings = get_spotify_episode_mapping()
            if spotify_episode_name in mappings:
                episode_id = mappings[spotify_episode_name]
                return f"https://open.spotify.com/episode/{episode_id}?t={sec}"
    
    # For other content types, try the original URI
    if spotify_uri:
        eid = spotify_uri.split(":")[-1]
        return f"https://open.spotify.com/episode/{eid}?t={sec}"
    
    # Fallback to player URL if no URI available
    player_url = metadata.get("spotify_player_url", "")
    if player_url:
        return player_url
    
    return ""

def main():
    """Convert JSON transcripts to CSV with one row per transcript line."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "episode_id","timestamp_sec","speaker","text",
                "episode_name","spotify_url"
            ],
        )
        writer.writeheader()

        for p in sorted(DATA_DIR.glob("*.json")):
            j = json.loads(p.read_text(encoding="utf-8"))
            ep_id = episode_id(j)
            ep_name = j.get("name", "")
            metadata = j.get("metadata", {})
            
            for item in j.get("transcript", []) or []:
                text = (item.get("content") or "").strip()
                if not text:
                    continue
                ts = ns_to_sec(item.get("timestamp", 0))
                writer.writerow({
                    "episode_id": ep_id,
                    "timestamp_sec": ts,
                    "speaker": (item.get("actor") or "").strip(),
                    "text": text,
                    "episode_name": ep_name,
                    "spotify_url": spotify_url(metadata, ts, ep_id),
                })
    print(f"Wrote {OUT_FILE}")

if __name__ == "__main__":
    main()
