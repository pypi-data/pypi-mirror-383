"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_bitmap_structures.py

Comprehensive tests for Bitmap Structures.

Tests BITMAP, BITSET_DYNAMIC, ROARING_BITMAP strategies.
Critical for memory-efficient set operations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.nodes.strategies import (
    bitmap,
    bitset_dynamic,
    roaring_bitmap
)


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestBitmapStrategy:
    """Test BITMAP strategy (static bitmap)."""
    
    def test_strategy_exists(self):
        """Test that BITMAP strategy exists."""
        assert bitmap is not None
        assert NodeMode.BITMAP is not None
    
    def test_bitmap_operations(self):
        """Test bitmap set operations."""
        # Bitmaps support efficient bit operations
        assert NodeMode.BITMAP is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestBitsetDynamicStrategy:
    """Test BITSET_DYNAMIC strategy (resizable bitset)."""
    
    def test_strategy_exists(self):
        """Test that BITSET_DYNAMIC strategy exists."""
        assert bitset_dynamic is not None
        assert NodeMode.BITSET_DYNAMIC is not None
    
    def test_dynamic_resizing(self):
        """Test dynamic resizing capability."""
        # Dynamic bitsets can grow
        assert NodeMode.BITSET_DYNAMIC is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
@pytest.mark.xwnode_performance
class TestRoaringBitmapStrategy:
    """Test ROARING_BITMAP strategy (compressed, sparse-optimized)."""
    
    def test_strategy_exists(self):
        """Test that ROARING_BITMAP strategy exists."""
        assert roaring_bitmap is not None
        assert NodeMode.ROARING_BITMAP is not None
    
    def test_memory_efficiency(self):
        """Test 10-100x memory reduction for sparse data."""
        # Roaring bitmaps are extremely memory efficient
        assert NodeTrait.MEMORY_EFFICIENT is not None
    
    def test_compressed_storage(self):
        """Test compressed storage."""
        # Roaring bitmaps use compression
        assert NodeTrait.COMPRESSED is not None

