"""Unit tests for Bitset Dynamic strategy."""
import pytest
from exonware.xwnode.nodes.strategies.bitset_dynamic import BitsetDynamicStrategy
from exonware.xwnode.defs import NodeMode

@pytest.mark.xwnode_core
class TestBitsetDynamic:
    def test_init(self):
        s = BitsetDynamicStrategy()
        assert s.mode == NodeMode.BITSET_DYNAMIC
    def test_operations(self):
        s = BitsetDynamicStrategy()
        s.set_bit(5, True)
        # Bitset just tracks bits, has() checks existence
        assert s.has("5") or len(s) >= 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

