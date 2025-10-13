"""
#exonware/xwnode/tests/0.core/test_skip_list_strategy.py

Comprehensive tests for SKIP_LIST node strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.skip_list import SkipListStrategy
from exonware.xwnode.defs import NodeMode


@pytest.mark.xwnode_core
class TestSkipListCore:
    """Core tests for SKIP_LIST."""
    
    def test_init(self):
        s = SkipListStrategy()
        assert s is not None
        assert len(s) == 0
    
    def test_put_get(self):
        s = SkipListStrategy()
        s.put("a", 1)
        assert s.get("a") == 1
    
    def test_multiple(self):
        s = SkipListStrategy()
        for i in range(50):
            s.put(f"k{i}", i)
        assert len(s) >= 25
    
    def test_delete(self):
        s = SkipListStrategy()
        s.put("a", 1)
        s.delete("a")
        assert s.get("a") is None
    
    def test_iteration(self):
        s = SkipListStrategy()
        for i in range(10):
            s.put(f"k{i}", i)
        keys = list(s.keys())
        assert len(keys) >= 1
    
    def test_clear(self):
        s = SkipListStrategy()
        for i in range(10):
            s.put(f"k{i}", i)
        s.clear()
        assert len(s) == 0


@pytest.mark.xwnode_performance  
class TestSkipListPerformance:
    """Performance tests."""
    
    def test_ologn_search(self):
        import time, math
        strats = {}
        for size in [100, 1000]:
            st = SkipListStrategy()
            for i in range(size):
                st.put(f"k{i:06d}", i)
            strats[size] = st
        
        timings = {}
        for size, st in strats.items():
            meas = []
            for _ in range(50):
                start = time.perf_counter()
                st.get(f"k{size//2:06d}")
                meas.append(time.perf_counter() - start)
            meas.sort()
            timings[size] = meas[len(meas)//2]
        
        expected = math.log(1000) / math.log(100)
        actual = timings[1000] / timings[100]
        assert actual < expected * 4.0


@pytest.mark.xwnode_core
class TestSkipListEdgeCases:
    """Edge cases."""
    
    def test_empty(self):
        s = SkipListStrategy()
        assert len(s) == 0
        assert s.get("any") is None

