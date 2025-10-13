"""Unit tests for Masstree strategy."""
import pytest
from exonware.xwnode.nodes.strategies.masstree import MasstreeStrategy
from exonware.xwnode.defs import NodeMode

@pytest.mark.xwnode_core
class TestMasstree:
    def test_init(self):
        s = MasstreeStrategy()
        assert s.mode == NodeMode.MASSTREE
    def test_operations(self):
        s = MasstreeStrategy()
        s.put("k", "v")
        assert s.get("k") == "v"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

