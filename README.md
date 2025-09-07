# XFM Quote Finder

A React + FastAPI application for searching through XFM episodes, podcasts, and guides using PostgreSQL full-text search.

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
   # For local development (SQLite)
   uv run python scripts/csv_to_sqlite.py
   
   # For production (PostgreSQL)
   uv run python scripts/csv_to_postgres.py
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
   - `DATABASE_URL`: (Railway will provide this automatically when you add PostgreSQL)
   - `PORT`: `8000` (Railway will set this automatically)

3. **Deploy:**
   - Railway will automatically detect the Python/FastAPI setup
   - The build process will install dependencies and build the frontend
   - Your app will be available at the provided Railway URL

4. **Database setup:**
   - Add PostgreSQL service in Railway
   - Railway will automatically provide `DATABASE_URL`
   - Run the import script: `python scripts/csv_to_postgres.py`

## Features

- **Full-text search** using PostgreSQL with optimized indexing
- **Speaker filtering** (Ricky, Steve, Karl)
- **Episode information** with Spotify links
- **Modern React UI** with Tailwind CSS
- **FastAPI backend** with automatic API documentation

## Tech Stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
- **Backend:** FastAPI, PostgreSQL with full-text search, Uvicorn
- **Deployment:** Railway (full-stack hosting)
- **Search:** PostgreSQL full-text search with GIN indexes

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

The application supports both SQLite (development) and PostgreSQL (production):

**Development (SQLite):**
1. Run `uv run python scripts/csv_to_sqlite.py` to create the database
2. Set `DATABASE_URL="sqlite:///./out/quotes.db"` for local testing

**Production (PostgreSQL):**
1. Set `DATABASE_URL` environment variable (Railway provides this automatically)
2. Run `uv run python scripts/csv_to_postgres.py` to import data
3. Database will be automatically initialized with optimized indexes

### Testing

```bash
# Run Python tests
uv run pytest

# Run frontend tests (if configured)
npm test
```

## License

This project is for educational and personal use.
