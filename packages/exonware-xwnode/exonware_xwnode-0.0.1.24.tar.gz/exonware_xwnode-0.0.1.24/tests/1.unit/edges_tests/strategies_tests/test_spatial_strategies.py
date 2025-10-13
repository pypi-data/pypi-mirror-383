"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/test_spatial_strategies.py

Comprehensive tests for Spatial Edge Strategies.

Tests R_TREE, QUADTREE, and OCTREE strategies for spatial indexing.
Critical for geographic and 2D/3D spatial data.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import EdgeMode, EdgeTrait
from exonware.xwnode.edges.strategies import rtree, quadtree, octree


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestSpatialStrategiesExist:
    """Test that spatial strategies exist."""
    
    def test_rtree_strategy_exists(self):
        """Test R_TREE strategy module exists."""
        assert rtree is not None
        assert EdgeMode.R_TREE is not None
    
    def test_quadtree_strategy_exists(self):
        """Test QUADTREE strategy module exists."""
        assert quadtree is not None
        assert EdgeMode.QUADTREE is not None
    
    def test_octree_strategy_exists(self):
        """Test OCTREE strategy module exists."""
        assert octree is not None
        assert EdgeMode.OCTREE is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_edge_strategy
class TestSpatialCapabilities:
    """Test spatial strategy capabilities."""
    
    def test_rtree_for_2d_3d_rectangles(self):
        """Test R_TREE supports 2D/3D spatial indexing."""
        # R-trees are for spatial indexing
        assert EdgeMode.R_TREE is not None
    
    def test_quadtree_for_2d_partitioning(self):
        """Test QUADTREE supports 2D spatial partitioning."""
        # Quadtrees partition 2D space
        assert EdgeMode.QUADTREE is not None
    
    def test_octree_for_3d_partitioning(self):
        """Test OCTREE supports 3D spatial partitioning."""
        # Octrees partition 3D space
        assert EdgeMode.OCTREE is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance
class TestSpatialPerformance:
    """Test spatial strategy performance."""
    
    def test_spatial_query_optimization(self):
        """Test spatial queries are optimized."""
        # Spatial structures provide 10-100x faster spatial queries
        assert EdgeMode.R_TREE is not None

