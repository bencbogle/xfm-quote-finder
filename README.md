# XFM Quote Finder - React Frontend

A modern, accessible React frontend for the XFM Quote Finder application.

## Features

- 🎨 **Minimal, airy design** with slate greys and emerald accents
- 🔍 **Fast full-text search** using SQLite FTS5 with highlighted matched terms
- 🎵 **Spotify integration** with direct episode links
- 📊 **Search analytics** with query logging and insights
- ⌨️ **Keyboard shortcuts** (`/` to focus search, `Enter` to search)
- ♿ **Accessible** with proper ARIA labels and focus management
- 📱 **Responsive** design that works on all devices
- ⚡ **Fast** with optimized loading states and error handling

## Tech Stack

- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Vite** for build tooling
- **Inter font** for typography

## Getting Started

### Frontend Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment:**
   ```bash
   cp env.example .env
   # Edit .env to set your API URL
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Build for production:**
   ```bash
   npm run build
   ```

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   uv sync
   ```

2. **Generate SQLite database:**
   ```bash
   uv run python scripts/csv_to_sqlite.py
   ```

3. **Start FastAPI server:**
   ```bash
   uv run uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
   ```

### Analytics

View search analytics:
```bash
uv run python scripts/analytics.py
```

## Environment Variables

- `VITE_API_URL` - Backend API URL (default: `http://localhost:8000`)

## Project Structure

```
src/
├── components/          # React components
│   ├── Header.tsx      # App header with logo
│   ├── SearchBar.tsx   # Search input with icon
│   ├── SpeakerFilter.tsx # Speaker dropdown filter
│   ├── StatsBar.tsx    # Statistics display
│   ├── ResultsList.tsx # Results container
│   ├── ResultCard.tsx  # Individual result card
│   ├── LoadingSkeleton.tsx # Loading state
│   ├── EmptyState.tsx  # No results state
│   └── Toast.tsx       # Error notifications
├── hooks/              # Custom React hooks
├── types.ts           # TypeScript type definitions
├── api.ts             # API functions
├── App.tsx            # Main app component
└── main.tsx           # App entry point
```

## Design System

### Colors
- **Slate greys** for text and backgrounds
- **Emerald** for actions and accents
- **Orange** reserved for logo only

### Typography
- **Inter font** with system fallbacks
- **H1**: 36px/44px line-height
- **H2**: 20px/28px line-height  
- **Body**: 16px/24px line-height

### Spacing
- **Container**: max-width 48rem (3xl)
- **Sections**: 24-32px gaps
- **Cards**: 20-24px padding

## Accessibility

- Proper ARIA labels and roles
- Keyboard navigation support
- Focus management
- Screen reader friendly
- High contrast ratios
- Semantic HTML structure

## API Integration

The frontend integrates with the existing FastAPI backend:

- `GET /search?q=query&speaker=speaker` - Search quotes
- `GET /stats` - Get statistics
- Spotify deep links for each result

## Development

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```
