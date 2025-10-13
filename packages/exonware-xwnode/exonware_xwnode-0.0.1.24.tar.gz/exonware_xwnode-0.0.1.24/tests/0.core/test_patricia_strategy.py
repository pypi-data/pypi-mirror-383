"""Unit tests for Patricia strategy."""
import pytest
from exonware.xwnode.nodes.strategies.patricia import PatriciaStrategy
from exonware.xwnode.defs import NodeMode

@pytest.mark.xwnode_core
class TestPatricia:
    def test_init(self):
        s = PatriciaStrategy()
        assert s.mode == NodeMode.PATRICIA
    def test_operations(self):
        s = PatriciaStrategy()
        s.put("key", "val")
        assert s.get("key") == "val"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

