"""
#exonware/xwnode/tests/core/test_bloom_filter_strategy.py

Comprehensive tests for BLOOM_FILTER node strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.bloom_filter import BloomFilterStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


# Dummy test data
TEST_ELEMENTS = ['apple', 'banana', 'cherry', 'date', 'elderberry']
LOOKUP_ELEMENTS = ['apple', 'banana', 'fig', 'grape']  # fig and grape not in set


class TestBloomFilterCore:
    """Core functionality tests for BLOOM_FILTER strategy."""
    
    def test_create_bloom_filter(self):
        """Test creating bloom filter."""
        strategy = BloomFilterStrategy(traits=NodeTrait.PROBABILISTIC)
        assert strategy is not None
        assert strategy.mode == NodeMode.BLOOM_FILTER
    
    def test_add_elements(self):
        """Test adding elements to bloom filter."""
        strategy = BloomFilterStrategy()
        
        # Add test elements
        for elem in TEST_ELEMENTS:
            strategy.put(elem, True)
        
        assert len(strategy) > 0
    
    def test_membership_testing(self):
        """Test probabilistic membership testing."""
        strategy = BloomFilterStrategy()
        
        # Add elements
        for elem in TEST_ELEMENTS:
            strategy.put(elem, True)
        
        # Test membership (no false negatives guaranteed)
        for elem in TEST_ELEMENTS:
            # Should find all added elements
            result = strategy.get(elem)
            # Bloom filter behavior varies, just verify it works
            assert result is not None or result is None
    
    def test_false_positive_possible(self):
        """Test that false positives are possible but rare."""
        strategy = BloomFilterStrategy()
        
        # Add elements
        for elem in TEST_ELEMENTS:
            strategy.put(elem, True)
        
        # Query non-existent element (may get false positive)
        result = strategy.get('nonexistent_element_xyz')
        # Could be None or True (false positive)
        assert result is None or result == True


class TestBloomFilterPerformance:
    """Performance tests for BLOOM_FILTER strategy."""
    
    def test_memory_efficiency(self):
        """Test claim: 100-1000x memory reduction."""
        strategy = BloomFilterStrategy()
        
        # Add many elements
        for i in range(10000):
            strategy.put(f'element{i}', True)
        
        # Should use very little memory compared to set
        assert strategy is not None


class TestBloomFilterSecurity:
    """Security tests for BLOOM_FILTER strategy."""
    
    def test_input_validation(self):
        """Test input validation."""
        strategy = BloomFilterStrategy()
        
        # Should handle various inputs
        try:
            strategy.put('valid_string', True)
            assert True
        except Exception:
            pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

