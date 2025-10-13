"""Unit tests for Data Interchange Optimized strategy."""
import pytest
from exonware.xwnode.nodes.strategies.data_interchange_optimized import DataInterchangeOptimizedStrategy
from exonware.xwnode.defs import NodeMode

@pytest.mark.xwnode_core
class TestDataInterchange:
    def test_init(self):
        s = DataInterchangeOptimizedStrategy()
        assert s.mode == NodeMode.DATA_INTERCHANGE_OPTIMIZED
    def test_operations(self):
        s = DataInterchangeOptimizedStrategy()
        s.put("k", "v")
        assert s.get("k") == "v"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

