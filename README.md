# XFM Quote Finder

Search XFM/Ricky–Steve–Karl podcast quotes and jump to the exact episode timestamp.

## Quickstart

```bash
# 1) Install deps
uv add rapidfuzz fastapi uvicorn

# 2) Convert JSON → CSV
uv run python scripts/json_to_csv.py

# 3) CLI search
uv run python cli/search_quotes.py "knob at night"

# 4) (Optional) Run API
uv run uvicorn app.main:app --reload
# GET http://127.0.0.1:8000/search?q=knob%20at%20night
