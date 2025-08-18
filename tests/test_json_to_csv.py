# Quick test that CSV gets created and has expected columns.
from pathlib import Path
import subprocess, csv

def test_json_to_csv_creates_file(tmp_path, monkeypatch):
    """Test that CSV gets created and has expected columns."""
    # Arrange: copy a small sample into tmp data dir
    data_dir = tmp_path / "data"
    out_dir = tmp_path / "out"
    data_dir.mkdir()
    out_dir.mkdir()
    sample = data_dir / "sample.json"
    sample.write_text('{"publication":"xfm","series":1,"episode":12,"name":"Test","metadata":{"spotify_uri":"spotify:episode:abc"},"transcript":[{"timestamp":1000000000,"actor":"Karl","content":"Hello there"}]}', encoding="utf-8")

    # Act
    code = subprocess.call(["python", "scripts/json_to_csv.py"], cwd=tmp_path)
    assert code == 0

    # Assert
    out_csv = out_dir / "quotes.csv"
    assert out_csv.exists()
    rows = list(csv.DictReader(out_csv.open(encoding="utf-8")))
    assert rows and rows[0]["speaker"] == "Karl"
