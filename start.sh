#!/bin/bash
echo "Starting XFM Quote Finder..."
echo "Python version:"
python3 --version || python --version || echo "Python not found"
echo "Current directory:"
pwd
echo "Files in current directory:"
ls -la
echo "Trying to start uvicorn..."
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
