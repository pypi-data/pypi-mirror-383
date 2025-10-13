"""Unit tests for Ordered Map strategy."""
import pytest
from exonware.xwnode.nodes.strategies.ordered_map import OrderedMapStrategy
from exonware.xwnode.defs import NodeMode

@pytest.mark.xwnode_core
class TestOrderedMapCore:
    def test_init(self):
        s = OrderedMapStrategy()
        assert s.mode == NodeMode.ORDERED_MAP
    
    def test_put_get(self):
        s = OrderedMapStrategy()
        s.put("key", "val")
        assert s.get("key") == "val"
    
    def test_ordering(self):
        s = OrderedMapStrategy()
        s.put("c", 3)
        s.put("a", 1)
        s.put("b", 2)
        assert list(s.keys()) == ["a", "b", "c"]
    
    def test_delete(self):
        s = OrderedMapStrategy()
        s.put("k", "v")
        assert s.delete("k")
        assert not s.has("k")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

