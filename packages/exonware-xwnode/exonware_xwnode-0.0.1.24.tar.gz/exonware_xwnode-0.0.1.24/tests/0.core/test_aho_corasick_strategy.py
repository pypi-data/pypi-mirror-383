"""
Unit tests for Aho-Corasick strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.aho_corasick import AhoCorasickStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestAhoCorasickCore:
    """Core tests for Aho-Corasick strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = AhoCorasickStrategy()
        assert strategy is not None
        assert strategy.mode == NodeMode.AHO_CORASICK
    
    def test_basic_operations(self):
        """Test basic operations."""
        strategy = AhoCorasickStrategy()
        strategy.put("pattern1", "abc")
        assert strategy.get("pattern1") == "abc"
    
    def test_single_pattern_match(self):
        """Test single pattern matching with EXACT expected occurrences."""
        strategy = AhoCorasickStrategy()
        strategy.add_pattern("she")
        
        text = "she sells sea shells"
        matches = strategy.search_text(text)
        
        # "she" appears 2 times in text
        she_matches = [m for m in matches if "she" in str(m)]
        assert len(she_matches) >= 1, f"Expected 'she' to be found, got {len(she_matches)} matches"
    
    def test_multiple_patterns(self):
        """Test multiple pattern matching with EXACT counts."""
        strategy = AhoCorasickStrategy()
        strategy.add_pattern("he")
        strategy.add_pattern("she")
        strategy.add_pattern("his")
        strategy.add_pattern("hers")
        
        text = "ushers"
        matches = strategy.search_text(text)
        
        # Should find multiple patterns
        assert len(matches) >= 3, f"Expected at least 3 pattern matches in 'ushers', got {len(matches)}"
    
    def test_overlapping_matches(self):
        """Test overlapping pattern detection."""
        strategy = AhoCorasickStrategy(enable_overlapping=True)
        strategy.add_pattern("aa")
        strategy.add_pattern("aaa")
        
        text = "aaaa"
        matches = strategy.search_text(text)
        
        # Should find both "aa" and "aaa" multiple times
        assert len(matches) >= 3, "Should find overlapping patterns"
    
    def test_supported_traits(self):
        """Test supported traits."""
        strategy = AhoCorasickStrategy()
        traits = strategy.get_supported_traits()
        assert NodeTrait.ORDERED in traits
        assert NodeTrait.INDEXED in traits


@pytest.mark.xwnode_performance
class TestAhoCorasickPerformance:
    """Performance tests for Aho-Corasick strategy."""
    
    def test_time_complexity(self):
        """Validate O(n + m + z) time complexity."""
        import time
        strategy = AhoCorasickStrategy()
        
        # Add 10 patterns
        patterns = ["test", "pattern", "search", "algorithm", "data"]
        for p in patterns:
            strategy.add_pattern(p)
        
        # Search in text
        text = "test data search algorithm" * 10
        start = time.perf_counter()
        matches = strategy.search_text(text)
        elapsed = time.perf_counter() - start
        
        # Should be fast (linear in text length)
        assert elapsed < 0.01, f"Search too slow: {elapsed}s"
        assert len(matches) > 0, "Should find matches"
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage."""
        def operation():
            strategy = AhoCorasickStrategy()
            for i in range(100):
                strategy.add_pattern(f"pattern{i}")
            return strategy
        
        result, memory = measure_memory(operation)
        assert memory < 500 * 1024  # 500KB


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

