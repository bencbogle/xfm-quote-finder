# Minimal FastAPI with /search?q=... returning JSON results.
from fastapi import FastAPI, Query, HTTPException
from app.search_core import search_quotes

app = FastAPI(title="XFM Quote Finder")

@app.get("/search")
def search(q: str = Query(..., min_length=2), top_k: int = 5):
    """Search quotes with fuzzy matching."""
    try:
        results = search_quotes(q, top_k=top_k)
        return {"query": q, "count": len(results), "results": results}
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="quotes.csv not found. Run json_to_csv.py first.")
