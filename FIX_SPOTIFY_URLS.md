# Fix Spotify URL Mappings in Database

## Problem
The database contains incorrect Spotify URLs for quotes. Many quotes from different episodes are linking to the same wrong episode (likely S02E21). This happened because the episode mapping files were missing during the initial data import.

## Solution
Regenerate the CSV data with correct Spotify URLs using proper episode mappings, then re-import to the database.

## Steps to Fix

### 1. Generate Spotify Episode Mapping
Fetch all Spotify episodes and create the mapping file:
```bash
python scripts/fetch_spotify_episodes.py
```
This creates `spotify_episode_mapping.csv` with episode data from Spotify API.

### 2. Create Episode Mapping JSON
Map your data files to Spotify episodes:
```bash
python scripts/create_mapping.py
```
This creates `episode_mapping.json` that maps episode IDs (e.g., `podcast-s1e01`) to Spotify episode IDs.

**Note:** Both scripts require:
- Spotify API credentials (CLIENT_ID and CLIENT_SECRET) if fetching from API
- Or existing `spotify_episode_mapping.csv` file if you have one

### 3. Regenerate CSV with Correct URLs
Convert JSON transcripts to CSV with proper Spotify URLs:
```bash
python scripts/json_to_csv.py
```
This reads from `data/*.json` files and creates `out/quotes.csv` with correct Spotify URLs using the mapping files.

**Verify:** Check that the CSV contains correct Spotify URLs before proceeding.

### 4. Re-import to Database
Clear existing data and import the corrected CSV:
```bash
python scripts/csv_to_postgres.py
```
This script:
- Deletes all existing quotes from the database
- Imports quotes from `out/quotes.csv`
- Skips episodes without Spotify URLs (Best Of episodes)
- Shows progress during import

### 5. Verify the Fix
Test a few searches to confirm Spotify links now point to the correct episodes:
- Search for quotes from "The Future" episode - should link to that episode, not "Law and Order"
- Check multiple episodes to ensure mappings are correct

## Files Involved

- `scripts/fetch_spotify_episodes.py` - Fetches Spotify episode data
- `scripts/create_mapping.py` - Creates episode mapping JSON
- `scripts/json_to_csv.py` - Converts JSON to CSV with Spotify URLs (already fixed to not use hardcoded fallback)
- `scripts/csv_to_postgres.py` - Imports CSV to PostgreSQL (already improved with batch processing)
- `spotify_episode_mapping.csv` - Generated mapping file (needs to be created)
- `episode_mapping.json` - Generated mapping file (needs to be created)
- `out/quotes.csv` - Generated CSV file (needs to be regenerated)

## Important Notes

- The code in `scripts/json_to_csv.py` has already been fixed to return empty strings instead of wrong episode IDs when mappings aren't found
- This fix prevents future wrong URLs, but doesn't fix existing database data
- You MUST regenerate and re-import the data to fix existing incorrect URLs
- Make sure you have access to the original JSON transcript files in the `data/` directory
- Back up your database before running `csv_to_postgres.py` if you want to preserve existing data

