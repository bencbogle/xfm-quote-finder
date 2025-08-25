# Minimal FastAPI with /search?q=... returning JSON results.
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.search_core import search_quotes
import os

app = FastAPI(title="XFM Quote Finder")

@app.get("/api/search")
def search(q: str = Query(..., min_length=2), top_k: int = 5, speaker: str = None):
    """Search quotes with fuzzy matching."""
    try:
        results = search_quotes(q, top_k=top_k, speaker_filter=speaker)
        return {"query": q, "count": len(results), "results": results}
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="quotes.csv not found. Run json_to_csv.py first.")

@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "message": "XFM Quote Finder API"}

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
