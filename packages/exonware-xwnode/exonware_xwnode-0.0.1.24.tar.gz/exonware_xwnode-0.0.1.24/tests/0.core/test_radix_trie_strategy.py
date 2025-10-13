"""Unit tests for Radix Trie strategy."""
import pytest
from exonware.xwnode.nodes.strategies.radix_trie import RadixTrieStrategy
from exonware.xwnode.defs import NodeMode

@pytest.mark.xwnode_core
class TestRadixTrie:
    def test_init(self):
        s = RadixTrieStrategy()
        assert s.mode == NodeMode.RADIX_TRIE
    def test_operations(self):
        s = RadixTrieStrategy()
        s.put("key", "val")
        assert s.get("key") == "val"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

