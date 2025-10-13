"""Unit tests for Bitmap strategy."""
import pytest
from exonware.xwnode.nodes.strategies.bitmap import BitmapStrategy
from exonware.xwnode.defs import NodeMode

@pytest.mark.xwnode_core
class TestBitmap:
    def test_init(self):
        s = BitmapStrategy()
        assert s.mode == NodeMode.BITMAP
    def test_operations(self):
        s = BitmapStrategy()
        s.set_bit(10)
        assert s.get_bit(10)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

