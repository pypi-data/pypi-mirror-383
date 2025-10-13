"""Unit tests for Set Tree strategy."""
import pytest
from exonware.xwnode.nodes.strategies.set_tree import SetTreeStrategy
from exonware.xwnode.defs import NodeMode

@pytest.mark.xwnode_core
class TestSetTreeCore:
    def test_init(self):
        s = SetTreeStrategy()
        assert s.mode == NodeMode.SET_TREE
        assert len(s) == 0
    
    def test_add(self):
        s = SetTreeStrategy()
        s.add("a")
        s.add("b")
        assert len(s) == 2
        assert "a" in s
    
    def test_duplicates(self):
        s = SetTreeStrategy()
        s.add("x")
        s.add("x")
        assert len(s) == 1
    
    def test_remove(self):
        s = SetTreeStrategy()
        s.add("item")
        assert s.remove("item")
        assert len(s) == 0
    
    def test_ordered(self):
        s = SetTreeStrategy()
        for x in ["c", "a", "b"]:
            s.add(x)
        assert list(s.keys()) == ["a", "b", "c"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

