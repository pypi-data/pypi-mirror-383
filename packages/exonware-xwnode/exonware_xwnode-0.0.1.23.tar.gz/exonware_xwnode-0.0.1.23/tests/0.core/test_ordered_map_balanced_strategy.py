"""Unit tests for Ordered Map Balanced strategy."""
import pytest
from exonware.xwnode.nodes.strategies.ordered_map_balanced import OrderedMapBalancedStrategy
from exonware.xwnode.defs import NodeMode

@pytest.mark.xwnode_core
class TestOrderedMapBalanced:
    def test_init(self):
        s = OrderedMapBalancedStrategy()
        assert s.mode == NodeMode.ORDERED_MAP_BALANCED
    def test_operations(self):
        s = OrderedMapBalancedStrategy()
        s.put("b", 2)
        s.put("a", 1)
        assert list(s.keys()) == ["a", "b"]
        assert s.get("a") == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

