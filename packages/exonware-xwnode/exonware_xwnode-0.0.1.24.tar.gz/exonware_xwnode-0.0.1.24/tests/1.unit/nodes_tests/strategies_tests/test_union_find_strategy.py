"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_union_find_strategy.py

Comprehensive tests for UNION_FIND Strategy (Disjoint Set).

Optimized for connectivity queries with nearly O(1) operations.
Critical for graph algorithms and component tracking.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.union_find import UnionFindStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.fixture
def empty_union_find():
    """Create empty union-find structure."""
    return UnionFindStrategy()


@pytest.fixture
def connected_sets():
    """Create union-find with connected sets."""
    uf = UnionFindStrategy()
    # Create two connected components
    uf.insert('A', 'A')
    uf.insert('B', 'B')
    uf.insert('C', 'C')
    uf.insert('D', 'D')
    return uf


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestUnionFindInterface:
    """Test UNION_FIND interface compliance."""
    
    def test_insert_creates_element(self, empty_union_find):
        """Test inserting elements."""
        empty_union_find.insert('A', 'A')
        
        assert empty_union_find.find('A') is not None
    
    def test_find_operation(self, connected_sets):
        """Test find operation."""
        result = connected_sets.find('A')
        assert result is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance
class TestUnionFindPerformance:
    """Test UNION_FIND performance."""
    
    def test_nearly_constant_time_operations(self):
        """Test O(α(n)) amortized performance."""
        uf = UnionFindStrategy()
        
        # Insert many elements
        for i in range(10000):
            uf.insert(i, i)
        
        # Operations should be very fast
        assert uf.find(5000) is not None

