# XFM Quote Finder

A React + FastAPI application for searching through XFM episodes, podcasts, and guides using SQLite FTS5 full-text search.

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   # Frontend
   npm install
   
   # Backend
   uv sync
   ```

2. **Set up the database:**
   ```bash
   uv run python scripts/csv_to_sqlite.py
   ```

3. **Run the development servers:**
   ```bash
   # Terminal 1: Backend
   uv run python -m uvicorn app.main:app --reload
   
   # Terminal 2: Frontend
   npm run dev
   ```

4. **Open your browser:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### Railway Deployment

1. **Connect your GitHub repository to Railway:**
   - Go to [Railway](https://railway.app)
   - Create a new project
   - Connect your GitHub repository

2. **Set environment variables in Railway:**
   - `DATABASE_PATH`: `/data/quotes.db` (Railway persistent storage)
   - `PORT`: `8000` (Railway will set this automatically)

3. **Deploy:**
   - Railway will automatically detect the Python/FastAPI setup
   - The build process will install dependencies and build the frontend
   - Your app will be available at the provided Railway URL

4. **Database setup:**
   - Upload your `quotes.db` file to Railway's persistent storage
   - Or run the database setup scripts in Railway's console

## Features

- **Full-text search** using SQLite FTS5
- **Speaker filtering** (Ricky, Steve, Karl)
- **Episode information** with Spotify links
- **Modern React UI** with Tailwind CSS
- **FastAPI backend** with automatic API documentation

## Tech Stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
- **Backend:** FastAPI, SQLite with FTS5, Uvicorn
- **Deployment:** Railway (full-stack hosting)
- **Search:** SQLite FTS5 full-text search engine

## API Endpoints

- `GET /api/search?q=<query>&top_k=<limit>&speaker=<speaker>` - Search quotes
- `GET /api/health` - Health check
- `GET /api/stats` - Get database statistics

## Development

### Project Structure

```
xfm-quote-finder/
├── app/                 # FastAPI backend
│   ├── main.py         # Main application entry point
│   ├── search_core.py  # Search functionality
│   └── api.py          # API endpoints
├── src/                # React frontend
│   ├── components/     # React components
│   ├── hooks/          # Custom React hooks
│   └── types.ts        # TypeScript types
├── scripts/            # Utility scripts
├── data/               # Data files
└── tests/              # Test files
```

### Database Setup

The application uses SQLite with FTS5 for full-text search. To set up the database:

1. Run `python scripts/csv_to_sqlite.py` to create the database
2. The database will be created at `out/quotes.db`

### Testing

```bash
# Run Python tests
uv run pytest

# Run frontend tests (if configured)
npm test
```

## License

This project is for educational and personal use.
