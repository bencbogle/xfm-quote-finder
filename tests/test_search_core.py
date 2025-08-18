# Test the fuzzy search returns something sensible.
from pathlib import Path
import csv
from app.search_core import search_quotes, load_rows

def test_search_core_simple(tmp_path, monkeypatch):
    """Test that search_quotes returns something sensible."""
    out = tmp_path / "out"
    out.mkdir()
    csv_path = out / "quotes.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["episode_id","timestamp_sec","speaker","text","episode_name","spotify_url"])
        w.writeheader()
        w.writerow({"episode_id":"xfm-s1e1","timestamp_sec":123,"speaker":"Karl","text":"I could eat a knob at night","episode_name":"Pilot","spotify_url":""})
    # point loader to tmp csv
    monkeypatch.setattr("app.search_core.CSV_PATH", csv_path)
    res = search_quotes("knob at night", top_k=3, min_score=50)
    assert res and "Karl" in res[0]["speaker"]
