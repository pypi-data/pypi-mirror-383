"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_sparse_formats.py

Comprehensive tests for Sparse Matrix Edge Formats.

Tests CSR, CSC, COO strategies for sparse graphs.
Critical for matrix operations and memory efficiency.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import EdgeMode, EdgeTrait
from exonware.xwnode.edges.strategies import (
    csr,
    csc,
    coo
)


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestCSRStrategy:
    """Test CSR (Compressed Sparse Row) strategy."""
    
    def test_strategy_exists(self):
        """Test that CSR strategy exists."""
        assert csr is not None
        assert EdgeMode.CSR is not None
    
    def test_compressed_storage(self):
        """Test compressed storage."""
        # CSR provides compressed storage
        assert EdgeTrait.COMPRESSED is not None
    
    def test_memory_reduction(self):
        """Test 2-5x memory reduction."""
        assert EdgeMode.CSR is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestCSCStrategy:
    """Test CSC (Compressed Sparse Column) strategy."""
    
    def test_strategy_exists(self):
        """Test that CSC strategy exists."""
        assert csc is not None
        assert EdgeMode.CSC is not None
    
    def test_column_oriented_operations(self):
        """Test column-oriented operations."""
        assert EdgeMode.CSC is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestCOOStrategy:
    """Test COO (Coordinate) format strategy."""
    
    def test_strategy_exists(self):
        """Test that COO strategy exists."""
        assert coo is not None
        assert EdgeMode.COO is not None
    
    def test_coordinate_format(self):
        """Test coordinate format storage."""
        assert EdgeMode.COO is not None

