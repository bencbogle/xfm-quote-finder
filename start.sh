#!/bin/bash
echo "Starting XFM Quote Finder..."
echo "Current directory:"
pwd
echo "Files in current directory:"
ls -la
echo "Trying to start uvicorn with uv..."
exec uv run python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
