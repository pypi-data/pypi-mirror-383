"""Unit tests for Learned Index strategy."""
import pytest
from exonware.xwnode.nodes.strategies.learned_index import LearnedIndexStrategy
from exonware.xwnode.defs import NodeMode

@pytest.mark.xwnode_core
class TestLearnedIndex:
    def test_init(self):
        s = LearnedIndexStrategy()
        assert s.mode == NodeMode.LEARNED_INDEX
    def test_operations(self):
        s = LearnedIndexStrategy()
        s.put("k", "v")
        assert s.get("k") == "v"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

