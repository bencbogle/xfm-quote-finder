#!/usr/bin/env python3
"""
FastAPI server for XFM Quote Finder.
Provides a simple HTTP API wrapper around the search functionality.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import List, Dict, Any
import uvicorn

from .search_core import search_quotes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="XFM Quote Finder API",
    description="Search through XFM episodes, podcasts, and guides",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "XFM Quote Finder API", "status": "healthy"}

@app.get("/search")
async def search_endpoint(q: str, limit: int = 5, speaker: str = None):
    """
    Search for quotes.
    
    Args:
        q: Search query
        limit: Maximum number of results (default: 5)
    
    Returns:
        List of matching quotes with episode info and Spotify URLs
    """
    try:
        # Validate speaker filter if provided
        valid_speakers = ["ricky", "steve", "karl"]
        speaker_filter = None
        if speaker:
            if speaker.lower() not in valid_speakers:
                raise HTTPException(status_code=400, detail=f"Invalid speaker. Must be one of: {', '.join(valid_speakers)}")
            speaker_filter = speaker.lower()
        
        logger.info(f"Search request: '{q}' (limit: {limit}, speaker: {speaker_filter or 'all'})")
        
        # Use existing search logic
        results = search_quotes(q, top_k=limit, min_score=80, speaker_filter=speaker_filter)
        

        
        # Format results for API response
        formatted_results = []
        for result in results:
            formatted_results.append({
                "score": result["score"],
                "episode_id": result["episode_id"],
                "episode_name": result["episode_name"],
                "timestamp_sec": result["timestamp_sec"],
                "timestamp_hms": result["timestamp_hms"],
                "speaker": result["speaker"],
                "text": result["text"],
                "spotify_url": result["spotify_url"]
            })
        
        logger.info(f"Found {len(formatted_results)} results for '{q}'")
        
        return {
            "query": q,
            "speaker_filter": speaker_filter,
            "results": formatted_results,
            "total_results": len(formatted_results)
        }
        
    except Exception as e:
        logger.error(f"Search error for query '{q}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get basic statistics about the search data."""
    try:
        from .search_core import load_rows
        rows = load_rows()
        
        # Count episodes
        episodes = set(row["episode_id"] for row in rows)
        
        # Count quotes
        total_quotes = len(rows)
        
        return {
            "total_quotes": total_quotes,
            "unique_episodes": len(episodes),
            "episodes": list(episodes)
        }
        
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
