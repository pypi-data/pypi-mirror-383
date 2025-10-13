"""Unit tests for Roaring Bitmap strategy."""
import pytest
from exonware.xwnode.nodes.strategies.roaring_bitmap import RoaringBitmapStrategy
from exonware.xwnode.defs import NodeMode

@pytest.mark.xwnode_core
class TestRoaringBitmap:
    def test_init(self):
        s = RoaringBitmapStrategy()
        assert s.mode == NodeMode.ROARING_BITMAP
    def test_operations(self):
        s = RoaringBitmapStrategy()
        s.put("0", 0)
        s.put("100", 100)
        assert s.has("0")
        assert s.has("100")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

