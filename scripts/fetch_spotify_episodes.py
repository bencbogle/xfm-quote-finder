#!/usr/bin/env python3
"""
One-time script to fetch all episodes from RSK XFM Spotify show and create episode mappings.
Requires spotipy library and Spotify API credentials.
"""

import csv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Spotify Show ID for RSK XFM
SHOW_ID = "34mXWuUCEa2UzTft5vxxLp"

def fetch_all_episodes():
    """Fetch all episodes from the RSK XFM Spotify show."""
    
    # Initialize Spotify client
    # You'll need to set these environment variables:
    # SPOTIPY_CLIENT_ID=your_client_id
    # SPOTIPY_CLIENT_SECRET=your_client_secret
    
    try:
        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    except Exception as e:
        print(f"Error initializing Spotify client: {e}")
        print("Please set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables")
        return None
    
    episodes = []
    offset = 0
    limit = 50  # Spotify API limit
    
    print(f"Fetching episodes from show {SHOW_ID}...")
    
    while True:
        try:
            # Get episodes from the show
            results = sp.show_episodes(SHOW_ID, limit=limit, offset=offset)
            
            if not results['items']:
                break
                
            for episode in results['items']:
                episodes.append({
                    'id': episode['id'],
                    'name': episode['name'],
                    'release_date': episode['release_date'],
                    'duration_ms': episode['duration_ms'],
                    'external_urls': episode['external_urls']['spotify']
                })
            
            print(f"Fetched {len(episodes)} episodes so far...")
            
            if len(results['items']) < limit:
                break
                
            offset += limit
            
        except Exception as e:
            print(f"Error fetching episodes: {e}")
            break
    
    return episodes

def parse_episode_info(episode_name):
    """Parse episode name to extract series and episode numbers."""
    # Examples: "S01E01", "S02E21", "S03E06"
    import re
    
    # Look for S##E## pattern
    match = re.search(r'S(\d+)E(\d+)', episode_name, re.IGNORECASE)
    if match:
        series = int(match.group(1))
        episode = int(match.group(2))
        return series, episode
    
    return None, None

def create_mapping_csv(episodes):
    """Create a CSV file with episode mappings."""
    
    output_file = Path("spotify_episode_mapping.csv")
    
    with output_file.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['episode_name', 'spotify_id', 'release_date', 'series', 'episode', 'spotify_url'])
        
        for ep in episodes:
            series, episode_num = parse_episode_info(ep['name'])
            
            writer.writerow([
                ep['name'],
                ep['id'],
                ep['release_date'],
                series or '',
                episode_num or '',
                ep['external_urls']
            ])
    
    print(f"Created mapping file: {output_file}")
    return output_file

def main():
    """Main function to fetch episodes and create mapping."""
    
    print("RSK XFM Spotify Episode Mapper")
    print("=" * 40)
    
    # Check for Spotify credentials
    if not os.getenv('SPOTIPY_CLIENT_ID') or not os.getenv('SPOTIPY_CLIENT_SECRET'):
        print("\n❌ Spotify API credentials not found!")
        print("Please set the following environment variables:")
        print("  SPOTIPY_CLIENT_ID=your_client_id")
        print("  SPOTIPY_CLIENT_SECRET=your_client_secret")
        print("\nYou can get these from: https://developer.spotify.com/dashboard")
        return
    
    # Fetch episodes
    episodes = fetch_all_episodes()
    
    if not episodes:
        print("❌ No episodes fetched!")
        return
    
    print(f"\n✅ Successfully fetched {len(episodes)} episodes")
    
    # Create mapping CSV
    mapping_file = create_mapping_csv(episodes)
    
    # Show summary
    print(f"\n📊 Summary:")
    print(f"  Total episodes: {len(episodes)}")
    
    # Count episodes by series
    series_counts = {}
    for ep in episodes:
        series, _ = parse_episode_info(ep['name'])
        if series:
            series_counts[series] = series_counts.get(series, 0) + 1
    
    for series in sorted(series_counts.keys()):
        print(f"  Series {series}: {series_counts[series]} episodes")
    
    print(f"\n📁 Mapping saved to: {mapping_file}")
    print("\nNext steps:")
    print("1. Review the mapping file")
    print("2. Update scripts/json_to_csv.py to use this mapping")
    print("3. Run the CSV generation again")

if __name__ == "__main__":
    main()
