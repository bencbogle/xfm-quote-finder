import os
import pytest

from app.search_core import search_quotes

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="DATABASE_URL not set - skipping database-dependent search tests",
)


def test_search_payload_structure():
    payload = search_quotes("knob", top_k=3)
    assert isinstance(payload, dict)
    assert "results" in payload
    assert "search_type" in payload
