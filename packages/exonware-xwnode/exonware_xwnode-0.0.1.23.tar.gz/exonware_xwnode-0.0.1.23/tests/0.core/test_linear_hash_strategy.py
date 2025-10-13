"""Unit tests for Linear Hash strategy."""
import pytest
from exonware.xwnode.nodes.strategies.linear_hash import LinearHashStrategy
from exonware.xwnode.defs import NodeMode

@pytest.mark.xwnode_core
class TestLinearHash:
    def test_init(self):
        s = LinearHashStrategy()
        assert s.mode == NodeMode.LINEAR_HASH
    def test_operations(self):
        s = LinearHashStrategy()
        s.put("k", "v")
        assert s.get("k") == "v"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

