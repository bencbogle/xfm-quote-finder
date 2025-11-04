"""
Tests for exact match search functionality.

These tests verify that specific known quotes are returned correctly
and that exact matches rank first.
"""
import pytest
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.search_core import search_quotes, normalize_query

# Skip tests if DATABASE_URL is not set
pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="DATABASE_URL not set - skipping database tests"
)


class TestExactMatches:
    """Test that exact phrase matches are found and ranked correctly."""
    
    def test_try_both_exact_match(self):
        """Test that 'Try both.' returns the exact match first."""
        results = search_quotes("Try both.", top_k=10, speaker_filter="karl")
        
        assert len(results) > 0, "Should return at least one result"
        assert results[0]["text"] == "Try both.", f"Expected 'Try both.' but got '{results[0]['text']}'"
        assert results[0]["episode_id"] == "xfm-s4e1", "Should be from episode xfm-s4e1"
        assert results[0]["speaker"] == "karl", "Should be by Karl"
        assert results[0]["rank"] > 100, "Exact match should have high rank"
    
    def test_try_both_no_punctuation(self):
        """Test that 'try both' (no punctuation) also finds the exact match."""
        results = search_quotes("try both", top_k=10, speaker_filter="karl")
        
        assert len(results) > 0, "Should return at least one result"
        # Should find "Try both." as exact match (normalized comparison)
        exact_match_found = any(
            normalize_query(r["text"]) == "try both" 
            for r in results
        )
        assert exact_match_found, "Should find exact match 'Try both.'"
    
    def test_cat_food_exact_match(self):
        """Test that 'cat food' returns the exact match first."""
        results = search_quotes("cat food", top_k=10, speaker_filter="karl")
        
        assert len(results) > 0, "Should return at least one result"
        # Check if exact match is in results (normalized)
        exact_match = next(
            (r for r in results if normalize_query(r["text"]) == "cat food"),
            None
        )
        assert exact_match is not None, "Should find exact match 'cat food'"
        # Exact match should be first
        assert normalize_query(results[0]["text"]) == "cat food", "Exact match should rank first"
        assert results[0]["rank"] > 100, "Exact match should have high rank"
    
    def test_exact_matches_rank_first(self):
        """Test that exact matches always rank above partial matches."""
        # Test with a query that has both exact and partial matches
        results = search_quotes("Try both.", top_k=20, speaker_filter="karl")
        
        if len(results) > 1:
            # Find exact matches
            exact_matches = [
                r for r in results 
                if normalize_query(r["text"]) == "try both"
            ]
            # Find partial matches (contain the words but not exact)
            partial_matches = [
                r for r in results 
                if normalize_query(r["text"]) != "try both"
            ]
            
            if exact_matches and partial_matches:
                # All exact matches should rank higher than all partial matches
                min_exact_rank = min(r["rank"] for r in exact_matches)
                max_partial_rank = max(r["rank"] for r in partial_matches)
                assert min_exact_rank > max_partial_rank, \
                    f"Exact matches (min rank: {min_exact_rank}) should rank above partial matches (max rank: {max_partial_rank})"
    
    def test_speaker_filter_works(self):
        """Test that speaker filter correctly filters results."""
        results_karl = search_quotes("Try both.", top_k=10, speaker_filter="karl")
        results_all = search_quotes("Try both.", top_k=10, speaker_filter=None)
        
        assert len(results_karl) > 0, "Should return results for Karl"
        assert all(r["speaker"] == "karl" for r in results_karl), \
            "All results should be from Karl when filtered"
        
        # Verify that the exact match appears in both (when it exists)
        karl_texts = {r["text"] for r in results_karl}
        all_texts = {r["text"] for r in results_all}
        
        # The exact match "Try both." should be in both if it exists
        if "Try both." in all_texts:
            assert "Try both." in karl_texts, \
                "Exact match 'Try both.' should appear in Karl-filtered results"
        
        # Verify all results are from the correct speaker
        assert all(r["speaker"] == "karl" for r in results_karl), \
            "All Karl-filtered results must be from Karl"


class TestPhraseMatching:
    """Test phrase matching behavior."""
    
    def test_phrase_query_detection(self):
        """Test that 2-4 word queries use phrase matching."""
        from app.search_core import is_phrase_query
        
        assert is_phrase_query("Try both.") == True
        assert is_phrase_query("try both") == True
        assert is_phrase_query("cat food") == True
        assert is_phrase_query("single") == False
        assert is_phrase_query("this is a very long query with many words") == False
    
    def test_single_word_fallback(self):
        """Test that single word queries still work."""
        results = search_quotes("knob", top_k=5, speaker_filter="karl")
        assert len(results) > 0, "Single word search should return results"


class TestNormalization:
    """Test query normalization."""
    
    def test_normalization_consistency(self):
        """Test that normalization is consistent."""
        test_cases = [
            ("Try both.", "try both"),
            ("try both", "try both"),
            ("TRY BOTH.", "try both"),
            ("Cat food", "cat food"),
        ]
        
        for input_query, expected_normalized in test_cases:
            normalized = normalize_query(input_query)
            assert normalized == expected_normalized, \
                f"'{input_query}' should normalize to '{expected_normalized}', got '{normalized}'"

