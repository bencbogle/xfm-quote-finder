#!/usr/bin/env bash
echo "Starting XFM Quote Finder..."
echo "Installing dependencies..."
python3 -m pip install --no-cache-dir -r requirements.txt
echo "Current directory:"
pwd
echo "Files in current directory:"
ls -la
echo "Trying to start uvicorn..."
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
