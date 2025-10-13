"""Unit tests for T-Tree strategy."""
import pytest
from exonware.xwnode.nodes.strategies.t_tree import TTreeStrategy
from exonware.xwnode.defs import NodeMode

@pytest.mark.xwnode_core
class TestTTree:
    def test_init(self):
        s = TTreeStrategy()
        assert s.mode == NodeMode.T_TREE
    def test_operations(self):
        s = TTreeStrategy()
        s.put("k", "v")
        assert s.get("k") == "v"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

