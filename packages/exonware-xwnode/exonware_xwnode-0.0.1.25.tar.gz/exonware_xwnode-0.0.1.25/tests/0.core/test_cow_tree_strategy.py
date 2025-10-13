"""Unit tests for COW Tree strategy."""
import pytest
from exonware.xwnode.nodes.strategies.cow_tree import COWTreeStrategy
from exonware.xwnode.defs import NodeMode

@pytest.mark.xwnode_core
class TestCOWTree:
    def test_init(self):
        s = COWTreeStrategy()
        assert s.mode == NodeMode.COW_TREE
    def test_operations(self):
        s = COWTreeStrategy()
        s.put("k", "v")
        assert s.get("k") == "v"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

