#!/bin/bash

# Start the FastAPI server
echo "Starting XFM Quote Finder API..."
uv run uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload &

# Wait a moment for the API to start
sleep 3

# Open the frontend in the default browser
echo "Opening frontend..."
open public/index.html

# Keep the script running
wait
