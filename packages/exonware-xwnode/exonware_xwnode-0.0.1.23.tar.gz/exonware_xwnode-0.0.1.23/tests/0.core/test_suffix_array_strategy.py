"""
Unit tests for Suffix Array strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.suffix_array import SuffixArrayStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestSuffixArrayCore:
    """Core tests for Suffix Array strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = SuffixArrayStrategy()
        assert strategy is not None
        assert strategy.mode == NodeMode.SUFFIX_ARRAY
    
    def test_basic_operations(self):
        """Test basic put/get operations."""
        strategy = SuffixArrayStrategy()
        strategy.put("text", "banana")
        assert strategy.get("text") == "banana"
    
    def test_pattern_search(self):
        """Test pattern search with EXACT expected occurrences."""
        strategy = SuffixArrayStrategy()
        text = "banana"
        strategy.put("text", text)
        
        # Search for "ana" - should occur at positions 1 and 3
        matches = strategy.search_pattern("ana")
        assert len(matches) == 2, f"Expected 2 occurrences of 'ana' in 'banana', got {len(matches)}"
        assert sorted(matches) == [1, 3], f"Expected positions [1,3], got {sorted(matches)}"
    
    def test_single_character_pattern(self):
        """Test single character search with EXACT counts."""
        strategy = SuffixArrayStrategy()
        strategy.put("text", "banana")
        
        # 'a' appears 3 times in "banana"
        matches = strategy.search_pattern("a")
        assert len(matches) == 3, f"Expected 3 occurrences of 'a', got {len(matches)}"
    
    def test_pattern_not_found(self):
        """Test pattern not found returns empty."""
        strategy = SuffixArrayStrategy()
        strategy.put("text", "banana")
        
        matches = strategy.search_pattern("xyz")
        assert len(matches) == 0, "Pattern 'xyz' should not be found"
    
    def test_case_sensitivity(self):
        """Test case-sensitive vs case-insensitive search."""
        case_sensitive = SuffixArrayStrategy(case_sensitive=True)
        case_sensitive.put("text", "BaNaNa")
        
        # Case sensitive: 'banana' != 'BaNaNa'
        matches = case_sensitive.search_pattern("ana")
        # Should find 0 (case sensitive)
        assert len(matches) == 0, "Case-sensitive should not find 'ana' in 'BaNaNa'"
        
        # Case insensitive
        case_insensitive = SuffixArrayStrategy(case_sensitive=False)
        case_insensitive.put("text", "BaNaNa")
        matches_insensitive = case_insensitive.search_pattern("ana")
        assert len(matches_insensitive) == 2, "Case-insensitive should find 2 'ana' in 'BaNaNa'"
    
    def test_clear_operation(self):
        """Test clear operation."""
        strategy = SuffixArrayStrategy()
        strategy.put("key", "value")
        strategy.clear()
        assert len(strategy) == 0
    
    def test_supported_traits(self):
        """Test supported traits."""
        strategy = SuffixArrayStrategy()
        traits = strategy.get_supported_traits()
        assert NodeTrait.ORDERED in traits
        assert NodeTrait.INDEXED in traits


@pytest.mark.xwnode_core
class TestSuffixArraySpecificFeatures:
    """Tests for Suffix Array specific features."""
    
    def test_multiple_patterns(self):
        """Test searching multiple patterns."""
        strategy = SuffixArrayStrategy()
        strategy.put("text", "abcabcabc")
        
        # "abc" appears 3 times
        matches_abc = strategy.search_pattern("abc")
        assert len(matches_abc) == 3, f"Expected 3 occurrences of 'abc', got {len(matches_abc)}"
        
        # "cab" appears 2 times
        matches_cab = strategy.search_pattern("cab")
        assert len(matches_cab) == 2, f"Expected 2 occurrences of 'cab', got {len(matches_cab)}"
    
    def test_overlapping_matches(self):
        """Test overlapping pattern matches."""
        strategy = SuffixArrayStrategy()
        strategy.put("text", "aaaa")
        
        # "aa" appears 3 times with overlap: positions 0, 1, 2
        matches = strategy.search_pattern("aa")
        assert len(matches) == 3, f"Expected 3 overlapping 'aa' in 'aaaa', got {len(matches)}"
    
    def test_longest_common_prefix(self):
        """Test LCP array if available."""
        strategy = SuffixArrayStrategy(enable_lcp=True)
        strategy.put("text", "banana")
        
        # Trigger build by searching
        matches = strategy.search_pattern("ana")
        
        # Verify it built successfully
        assert strategy._is_built, "Suffix array should be built after search"
        assert len(matches) == 2, "Should find pattern after build"


@pytest.mark.xwnode_performance
class TestSuffixArrayPerformance:
    """Performance tests for Suffix Array strategy."""
    
    def test_build_time(self):
        """Validate suffix array build time."""
        import time
        strategy = SuffixArrayStrategy()
        
        # Build with moderate text
        text = "abcdef" * 100  # 600 characters
        start = time.perf_counter()
        strategy.put("text", text)
        elapsed = time.perf_counter() - start
        
        # Build should be reasonably fast
        assert elapsed < 0.5, f"Build too slow: {elapsed}s for {len(text)} chars"
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage."""
        def operation():
            strategy = SuffixArrayStrategy()
            strategy.put("text", "banana" * 10)
            return strategy
        
        result, memory = measure_memory(operation)
        # Suffix array + LCP array
        assert memory < 500 * 1024  # 500KB


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

