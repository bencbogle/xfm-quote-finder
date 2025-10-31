#!/usr/bin/env python3
"""
Create mapping between data files and Spotify episodes.
This script reads the spotify_episode_mapping.csv and maps it to our data files.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple

def load_spotify_mappings() -> Dict[str, Dict]:
    """Load Spotify episode mappings from CSV."""
    mappings = {}
    
    with open("spotify_episode_mapping.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            episode_name = row["episode_name"]
            mappings[episode_name] = {
                "spotify_id": row["spotify_id"],
                "spotify_url": row["spotify_url"],
                "release_date": row["release_date"],
                "series": row["series"],
                "episode": row["episode"]
            }
    
    return mappings

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
        series_episode = episode_id.replace("guide-", "").upper()
        # Add leading zeros: S1E01 -> S01E01
        if "S" in series_episode and "E" in series_episode:
            parts = series_episode.split("E")
            series = parts[0]  # S1
            episode = parts[1]  # 01
            series_num = series[1:]  # 1
            episode_num = episode.zfill(2)  # 01
            series_episode = f"S{series_num.zfill(2)}E{episode_num}"  # S01E01
        
        # Map to specific guide titles
        guide_mappings = {
            "S01E01": "TRGS Guide to... Medicine",
            "S01E02": "TRGS Guide to... Natural History", 
            "S01E03": "TRGS Guide to... The Arts",
            "S01E04": "TRGS Guide to... Philosophy",
            "S01E05": "TRGS Guide to... Society",
            "S02E01": "TRGS Guide to... The English",
            "S02E02": "TRGS Guide to... The Future",
            "S02E03": "TRGS Guide to... Law & Order",
            "S02E04": "TRGS Guide to... The Earth",
            "S02E05": "TRGS Guide to... The Human Body",
            "S02E06": "TRGS Guide to... The World Cup",
            "S02E07": "TRGS Guide to... Armed Forces"
        }
        
        return guide_mappings.get(series_episode, f"TRGS Guide to... {series_episode}")
    
    return episode_id

def get_data_files() -> List[Path]:
    """Get all data files from the data directory."""
    data_dir = Path("data")
    return list(data_dir.glob("*.json"))

def convert_guide_name_to_spotify_format(episode_name: str) -> str:
    """Convert guide episode name from data file to Spotify format."""
    # "The Ricky Gervais Guide to: Medicine" -> "TRGS Guide to... Medicine"
    if episode_name.startswith("The Ricky Gervais Guide to:"):
        title = episode_name.replace("The Ricky Gervais Guide to:", "").strip()
        # Handle special case: "Law and Order" -> "Law & Order"
        if title == "Law and Order":
            title = "Law & Order"
        return f"TRGS Guide to... {title}"
    return episode_name

def create_mapping() -> List[Dict]:
    """Create the mapping between data files and Spotify episodes."""
    spotify_mappings = load_spotify_mappings()
    data_files = get_data_files()
    
    mapping_results = []
    
    for data_file in data_files:
        # Extract episode ID from filename (e.g., ep-xfm-S1E01.json -> xfm-s1e01)
        episode_id = data_file.stem.replace("ep-", "")
        
        # For guide episodes, read the actual name from the JSON file
        if episode_id.startswith("guide-"):
            try:
                import json
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    actual_name = data.get("name", "")
                    # Convert to Spotify format
                    spotify_episode_name = convert_guide_name_to_spotify_format(actual_name)
            except Exception as e:
                print(f"Warning: Could not read {data_file}: {e}")
                spotify_episode_name = convert_episode_name_to_spotify_format(episode_id)
        else:
            # For other episodes, use the existing conversion
            spotify_episode_name = convert_episode_name_to_spotify_format(episode_id)
        
        # Check if we have a mapping
        if spotify_episode_name in spotify_mappings:
            spotify_data = spotify_mappings[spotify_episode_name]
            mapping_results.append({
                "data_file": data_file.name,
                "episode_id": episode_id,
                "spotify_episode_name": spotify_episode_name,
                "spotify_id": spotify_data["spotify_id"],
                "spotify_url": spotify_data["spotify_url"],
                "mapped": True
            })
        else:
            mapping_results.append({
                "data_file": data_file.name,
                "episode_id": episode_id,
                "spotify_episode_name": spotify_episode_name,
                "spotify_id": "",
                "spotify_url": "",
                "mapped": False
            })
    
    return mapping_results

def save_mapping_csv(mapping_results: List[Dict], output_file: str = "episode_mapping.csv"):
    """Save mapping results to CSV."""
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "data_file", "episode_id", "spotify_episode_name", 
            "spotify_id", "spotify_url", "mapped"
        ])
        writer.writeheader()
        writer.writerows(mapping_results)

def save_mapping_json(mapping_results: List[Dict], output_file: str = "episode_mapping.json"):
    """Save mapping results to JSON."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(mapping_results, f, indent=2, ensure_ascii=False)

def main():
    """Main function to create and save the mapping."""
    print("Creating episode mapping...")
    
    mapping_results = create_mapping()
    
    # Save to CSV and JSON
    save_mapping_csv(mapping_results)
    save_mapping_json(mapping_results)
    
    # Print summary
    total_files = len(mapping_results)
    mapped_files = sum(1 for r in mapping_results if r["mapped"])
    unmapped_files = total_files - mapped_files
    
    print(f"\nMapping Summary:")
    print(f"Total data files: {total_files}")
    print(f"Successfully mapped: {mapped_files}")
    print(f"Unmapped: {unmapped_files}")
    print(f"Mapping success rate: {mapped_files/total_files*100:.1f}%")
    
    if unmapped_files > 0:
        print(f"\nUnmapped files:")
        for result in mapping_results:
            if not result["mapped"]:
                print(f"  {result['data_file']} -> {result['spotify_episode_name']}")
    
    print(f"\nMapping saved to:")
    print(f"  - episode_mapping.csv")
    print(f"  - episode_mapping.json")

if __name__ == "__main__":
    main()
