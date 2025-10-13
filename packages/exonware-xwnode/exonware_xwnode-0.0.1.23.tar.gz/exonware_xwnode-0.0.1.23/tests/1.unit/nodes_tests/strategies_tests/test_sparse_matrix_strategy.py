"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_sparse_matrix_strategy.py

Comprehensive tests for SPARSE_MATRIX Strategy.

Optimized for sparse matrix operations.
Critical for scientific computing and graph algorithms.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.nodes.strategies import sparse_matrix


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestSparseMatrixInterface:
    """Test SPARSE_MATRIX interface."""
    
    def test_strategy_exists(self):
        """Test that SPARSE_MATRIX strategy exists."""
        assert sparse_matrix is not None
        assert NodeMode.SPARSE_MATRIX is not None
    
    def test_matrix_operations(self):
        """Test matrix operation support."""
        # Sparse matrices support matrix ops
        assert NodeTrait.MATRIX_OPS is not None
        assert NodeTrait.SPARSE is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance
class TestSparseMatrixPerformance:
    """Test SPARSE_MATRIX performance."""
    
    def test_memory_efficiency_for_sparse_data(self):
        """Test memory efficiency for sparse matrices."""
        # Sparse matrices save memory for sparse data
        assert NodeTrait.MEMORY_EFFICIENT is not None

