# XFM Quote Finder

Just a free silly tool for the fans.

Search through quotes from the XFM radio show featuring Ricky Gervais, Stephen Merchant, and Karl Pilkington.

## What It Does

Search quotes by typing keywords or phrases. Filter results by speaker (Ricky, Steve, or Karl). Each result shows the episode name, timestamp, and a link to the episode on Spotify.

## How to Use

1. Type a search query in the search bar
2. Optionally filter by speaker using the filter buttons
3. Click on results to view the full quote with episode information

## How It's Built

**Frontend**: React + TypeScript, built with Vite, styled with Tailwind CSS

**Backend**: FastAPI (Python) with a REST API

**Search**: PostgreSQL full-text search using `to_tsvector` and `plainto_tsquery` with `ts_rank` for relevance scoring. Falls back to SQLite FTS5 with BM25 ranking if PostgreSQL isn't available.

**Database**: PostgreSQL (or SQLite for local development)

**Deployment**: Railway

## Feedback

Have suggestions or found a bug? [Open an issue on GitHub](https://github.com/bencbogle/xfm-quote-finder/issues).

## Acknowledgements

- **Transcripts** from [scrimpton.com](https://scrimpton.com/search)
- **Spotify uploads** by [RSK XFM Pilky01](https://open.spotify.com/show/34mXWuUCEa2UzTft5vxxLp?si=9caac35d12284346)
- Thanks to [Rhondson](https://www.reddit.com/user/Rhondson/) for remastering the episodes

## License

This project is for educational and personal use. All XFM content belongs to the original creators and rights holders.
