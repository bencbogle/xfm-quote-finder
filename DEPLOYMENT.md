# XFM Quote Finder - Deployment Guide

## Phase 1: Quick Demo Deployment

### Backend Deployment (Railway)

1. **Install Railway CLI** (if not already installed):
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize Railway project**:
   ```bash
   railway init
   ```

4. **Deploy**:
   ```bash
   railway up
   ```

5. **Get your backend URL**:
   ```bash
   railway domain
   ```

### Frontend Deployment (Vercel)

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Update API URL** in `public/index.html`:
   ```javascript
   const API_BASE_URL = 'https://your-railway-app.railway.app'; // Your Railway URL
   ```

3. **Deploy to Vercel**:
   ```bash
   cd public
   vercel --prod
   ```

### Alternative: Fly.io Deployment

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login to Fly**:
   ```bash
   fly auth login
   ```

3. **Create app**:
   ```bash
   fly launch
   ```

4. **Deploy**:
   ```bash
   fly deploy
   ```

## Environment Variables

Set these in your deployment platform:

- `SPOTIPY_CLIENT_ID`: Your Spotify API client ID
- `SPOTIPY_CLIENT_SECRET`: Your Spotify API client secret

## Production Considerations

### Database Migration
When you're ready to move from CSV to a proper database:

1. **Add PostgreSQL dependency**:
   ```bash
   uv add psycopg2-binary
   ```

2. **Update search_core.py** to use database instead of CSV
3. **Add database connection handling**

### CORS Configuration
Update CORS settings in `app/api.py` for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.vercel.app"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting
Add rate limiting for production:

```bash
uv add slowapi
```

Then in `app/api.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/search")
@limiter.limit("10/minute")
async def search_endpoint(request: Request, q: str, limit: int = 5):
    # ... existing code
```

## Monitoring

### Logging
The API includes basic logging. For production, consider:
- Structured logging with JSON format
- Log aggregation (e.g., Logtail, DataDog)
- Error tracking (e.g., Sentry)

### Health Checks
The `/` endpoint provides basic health checking. Consider adding:
- Database connectivity checks
- External service health (Spotify API)
- Response time monitoring

## Scaling

### Horizontal Scaling
- Railway/Fly.io handle this automatically
- Consider adding Redis for caching search results
- Implement database connection pooling

### Performance Optimization
- Add response caching for common searches
- Implement search result pagination
- Consider full-text search indexing (PostgreSQL FTS, Elasticsearch)
