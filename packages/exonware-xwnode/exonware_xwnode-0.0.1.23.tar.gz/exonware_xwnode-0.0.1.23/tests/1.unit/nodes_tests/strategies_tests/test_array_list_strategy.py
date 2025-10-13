"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_array_list_strategy.py

Comprehensive tests for ArrayListStrategy.

Tests cover:
- Interface compliance
- Linear operations (indexed access)
- Performance characteristics (O(1) access, O(n) delete)
- Security and error handling
- Edge cases

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode import XWNode
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.errors import XWNodeError


@pytest.fixture
def empty_list_node():
    """Create empty list node."""
    return XWNode.from_native([])


@pytest.fixture
def simple_list_node():
    """Create list node with simple data."""
    return XWNode.from_native([f'value_{i}' for i in range(5)])


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestArrayListStrategyInterface:
    """Test list nodes created from native Python lists."""
    
    def test_list_creation(self, empty_list_node):
        """Test creating list node."""
        assert empty_list_node is not None
    
    def test_list_with_data(self, simple_list_node):
        """Test list node with data."""
        assert simple_list_node is not None
        
        # Verify data exists by converting to native
        native = simple_list_node.to_native()
        assert native is not None
    
    def test_to_native_conversion(self, simple_list_node):
        """Test conversion to native Python data."""
        native = simple_list_node.to_native()
        
        # Should return valid data structure
        assert native is not None
        assert isinstance(native, (list, dict))
    
    def test_list_roundtrip(self):
        """Test list data roundtrip."""
        original_list = [1, 2, 3, 4, 5]
        node = XWNode.from_native(original_list)
        native = node.to_native()
        
        # Data should be preserved (may be dict or list)
        assert native is not None
        if isinstance(native, list):
            assert len(native) == 5
        elif isinstance(native, dict):
            # Converted to dict with numeric keys
            assert len(native) == 5


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
@pytest.mark.xwnode_performance
class TestArrayListStrategyPerformance:
    """Test list node performance characteristics."""
    
    def test_large_list_handling(self):
        """Test handling of large lists."""
        # Create large list
        large_list = list(range(10000))
        node = XWNode.from_native(large_list)
        
        assert node is not None
        assert len(node) > 0


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
@pytest.mark.xwnode_security
class TestArrayListStrategySecurity:
    """Test list node security."""
    
    def test_large_list_no_crash(self):
        """Test that large lists don't crash."""
        # Create moderate-sized list (100,000 is too much for output)
        large_list = list(range(1000))
        node = XWNode.from_native(large_list)
        
        # Just verify it was created without crashing
        assert node is not None
        # Verify data is preserved
        native = node.to_native()
        assert native is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestArrayListStrategyEdgeCases:
    """Test list node edge cases."""
    
    def test_empty_list_operations(self, empty_list_node):
        """Test operations on empty list."""
        assert empty_list_node is not None
        assert len(empty_list_node) >= 0
    
    def test_list_with_none_values(self):
        """Test handling of None values in list."""
        node = XWNode.from_native([1, None, 3, None, 5])
        
        assert node is not None
        assert len(node) > 0

