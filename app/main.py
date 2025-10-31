# FastAPI application with PostgreSQL backend
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from app.search_core import search_quotes, log_search, get_stats
from app.database import init_database

app = FastAPI(title="XFM Quote Finder")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables and indexes."""
    try:
        init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

@app.get("/api/search")
def search(
    request: Request,
    q: str = Query(..., min_length=2),
    top_k: int = 5,
    speaker: str = None,
    test: bool = Query(False, description="If true, skip logging this search")
):
    """Search quotes with PostgreSQL full-text search."""
    try:
        results = search_quotes(q, top_k=top_k, speaker_filter=speaker)
        
        # Log the search unless it's a test search
        if not test:
            # Extract IP address (handle proxies/load balancers)
            ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
            # X-Forwarded-For can contain multiple IPs, take the first one
            if ip and "," in ip:
                ip = ip.split(",")[0].strip()
            
            # Extract user agent
            user_agent = request.headers.get("User-Agent", "unknown")
            
            log_search(q, top_k, ip, user_agent)
        
        return {"query": q, "count": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "message": "XFM Quote Finder API"}

@app.get("/api/stats")
def stats():
    """Get database statistics."""
    try:
        return get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# Mount static files for the React frontend (after API routes)
if os.path.exists("dist"):
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")

# Serve index.html for all non-API routes (for SPA routing)
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Serve index.html for all other routes (SPA routing)
    if os.path.exists("dist/index.html"):
        return FileResponse("dist/index.html")
    else:
        return {"message": "Frontend not built. Run 'npm run build' first."}
