"""Unit tests for Extendible Hash strategy."""
import pytest
from exonware.xwnode.nodes.strategies.extendible_hash import ExtendibleHashStrategy
from exonware.xwnode.defs import NodeMode

@pytest.mark.xwnode_core
class TestExtendibleHash:
    def test_init(self):
        s = ExtendibleHashStrategy()
        assert s.mode == NodeMode.EXTENDIBLE_HASH
    def test_operations(self):
        s = ExtendibleHashStrategy()
        s.put("k", "v")
        assert s.get("k") == "v"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

