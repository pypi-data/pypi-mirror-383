"""Unit tests for Persistent Tree strategy."""
import pytest
from exonware.xwnode.nodes.strategies.persistent_tree import PersistentTreeStrategy
from exonware.xwnode.defs import NodeMode

@pytest.mark.xwnode_core
class TestPersistentTree:
    def test_init(self):
        s = PersistentTreeStrategy()
        assert s.mode == NodeMode.PERSISTENT_TREE
    def test_operations(self):
        s = PersistentTreeStrategy()
        s.put("k", "v")
        assert s.get("k") == "v"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

