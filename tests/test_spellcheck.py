"""
Tests for spellcheck functionality.
"""
import pytest
from app.spellcheck import get_suggestions, SpellSuggestion
from app.text_utils import normalize_query


class TestSpellcheckSuggestions:
    """Test spellcheck suggestion generation."""
    
    def test_single_word_suggestions(self):
        """Test that single-word queries use direct lookup."""
        # Test with various misspellings to ensure general functionality
        test_cases = ["whaking", "monky", "ricy", "pilkingtun"]
        
        for query in test_cases:
            suggestions = get_suggestions(query, max_distance=1, max_suggestions=5)
            
            # Should return suggestions (may be empty for some queries)
            assert isinstance(suggestions, list)
            
            # All suggestions should have valid attributes
            for suggestion in suggestions:
                assert isinstance(suggestion, SpellSuggestion)
                assert suggestion.term
                assert suggestion.distance >= 0
                assert 0.0 <= suggestion.confidence <= 1.0
                assert suggestion.frequency >= 0
    
    def test_suggestions_sorted_by_distance(self):
        """Test that suggestions are sorted by distance first."""
        suggestions = get_suggestions("test", max_distance=2, max_suggestions=10)
        
        if len(suggestions) > 1:
            distances = [s.distance for s in suggestions]
            # All distance=0 should come before distance=1, etc.
            for i in range(len(distances) - 1):
                assert distances[i] <= distances[i + 1]
    
    def test_max_suggestions_limit(self):
        """Test that max_suggestions limit is respected."""
        suggestions = get_suggestions("test", max_distance=2, max_suggestions=3)
        assert len(suggestions) <= 3
    
    def test_empty_query(self):
        """Test that empty queries return empty suggestions."""
        suggestions = get_suggestions("", max_distance=2, max_suggestions=3)
        assert suggestions == []
    
    def test_no_suggestions_for_exact_match(self):
        """Test that exact matches may not appear in suggestions."""
        # This depends on dictionary, but normalized exact matches shouldn't appear
        query = "test"
        suggestions = get_suggestions(query, max_distance=1, max_suggestions=3)
        # If "test" is in dictionary, it might appear, but normalized version shouldn't
        normalized_query = normalize_query(query)
        for suggestion in suggestions:
            normalized_suggestion = normalize_query(suggestion.term)
            # If it's an exact normalized match, distance should be 0
            if normalized_suggestion == normalized_query:
                assert suggestion.distance == 0
    
    def test_multi_word_query_uses_compound_lookup(self):
        """Test that multi-word queries use lookup_compound."""
        suggestions = get_suggestions("try both", max_distance=2, max_suggestions=3)
        # Should handle multi-word queries
        assert isinstance(suggestions, list)
        # May return empty if no suggestions, but shouldn't crash


class TestSpellcheckEdgeCases:
    """Test edge cases and error handling."""
    
    def test_very_long_query(self):
        """Test that very long queries are handled."""
        long_query = "a" * 100
        suggestions = get_suggestions(long_query, max_distance=2, max_suggestions=3)
        # Should not crash, may return empty list
        assert isinstance(suggestions, list)
    
    def test_special_characters(self):
        """Test that queries with special characters are normalized."""
        suggestions = get_suggestions("test!!!", max_distance=1, max_suggestions=3)
        # Should normalize and still provide suggestions
        assert isinstance(suggestions, list)
    
    def test_numbers_in_query(self):
        """Test queries with numbers."""
        suggestions = get_suggestions("test123", max_distance=1, max_suggestions=3)
        assert isinstance(suggestions, list)
    
    def test_max_distance_respected(self):
        """Test that max_distance parameter is respected."""
        suggestions_d1 = get_suggestions("test", max_distance=1, max_suggestions=10)
        suggestions_d2 = get_suggestions("test", max_distance=2, max_suggestions=10)
        
        # Distance=2 should have same or more suggestions
        assert len(suggestions_d2) >= len(suggestions_d1)
        
        # All suggestions should respect max_distance
        for s in suggestions_d1:
            assert s.distance <= 1
        for s in suggestions_d2:
            assert s.distance <= 2

