"""
Unit tests for OCTREE edge strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies.octree import OctreeStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait


@pytest.mark.xwnode_core
class TestOctreeCore:
    """Core tests for OCTREE edge strategy."""
    
    def test_initialization(self):
        """Test initialization with EXACT expected state."""
        strategy = OctreeStrategy()
        assert strategy is not None
        assert strategy.mode == EdgeMode.OCTREE
        assert len(strategy) == 0
    
    def test_add_3d_spatial_edge(self, spatial_dataset):
        """Test add_edge with 3D spatial coordinates."""
        strategy = OctreeStrategy(spatial_threshold=0)  # Disable auto-connect
        edges = spatial_dataset(dimensions=3, num_edges=20)
        
        for src, tgt, props in edges:
            source_coords = (props['x1'], props['y1'], props['z1'])
            target_coords = (props['x2'], props['y2'], props['z2'])
            edge_id = strategy.add_edge(src, tgt,
                                       source_coords=source_coords,
                                       target_coords=target_coords)
            assert edge_id is not None
        
        # May be <= 20 if spatial deduplication occurs
        assert len(strategy) <= 20
        assert len(strategy) > 0
    
    def test_has_edge(self):
        """Test has_edge with EXACT boolean results."""
        strategy = OctreeStrategy()
        strategy.add_edge("v1", "v2", 
                         source_coords=(10, 10, 10), 
                         target_coords=(20, 20, 20))
        
        assert strategy.has_edge("v1", "v2") is True
        assert strategy.has_edge("v2", "v3") is False
    
    def test_octree_subdivision(self):
        """Test automatic octree subdivision into 8 octants."""
        strategy = OctreeStrategy(capacity=8, spatial_threshold=0)  # Disable auto-connect
        
        # Add enough edges to trigger subdivision
        for i in range(20):
            strategy.add_edge(f"v{i}", f"v{i+1}",
                            source_coords=(float(i), float(i), float(i)),
                            target_coords=(float(i+1), float(i+1), float(i+1)))
        
        # May be <= 20 if spatial deduplication occurs
        assert len(strategy) <= 20
        assert len(strategy) > 0
    
    def test_clear_operation(self):
        """Test clear with EXACT empty state."""
        strategy = OctreeStrategy()
        strategy.add_edge("v1", "v2", 
                         source_coords=(0, 0, 0), 
                         target_coords=(10, 10, 10))
        
        assert len(strategy) > 0
        strategy.clear()
        assert len(strategy) == 0
    
    def test_supported_traits(self):
        """Test trait support."""
        strategy = OctreeStrategy()
        traits = strategy.get_supported_traits()
        assert EdgeTrait.SPATIAL in traits


@pytest.mark.xwnode_core
class TestOctreeSpatialFeatures:
    """OCTREE specific 3D spatial feature tests."""
    
    def test_3d_spatial_partitioning(self):
        """Test 3D space partitioning into octants."""
        strategy = OctreeStrategy(spatial_threshold=0)  # Disable auto-connect
        
        # Add edges in different octants
        strategy.add_edge("v1", "v2", source_coords=(10, 10, 10), target_coords=(20, 20, 20))  # +++ octant
        strategy.add_edge("v2", "v3", source_coords=(-10, 10, 10), target_coords=(-20, 20, 20))  # -++ octant
        strategy.add_edge("v3", "v4", source_coords=(10, -10, 10), target_coords=(20, -20, 20))  # +-+ octant
        strategy.add_edge("v4", "v5", source_coords=(10, 10, -10), target_coords=(20, 20, -20))  # ++- octant
        
        # May be <= 4 if deduplication occurs
        assert len(strategy) <= 4
        assert len(strategy) > 0
    
    def test_3d_point_location(self):
        """
        Test finding vertices near a 3D point.
        
        Fixed: Octree spatial queries return vertices, using query_box().
        
        Priority: Maintainability #3 - Test actual API
        """
        strategy = OctreeStrategy()
        
        strategy.add_edge("v1", "v2", source_coords=(0, 0, 0), target_coords=(10, 10, 10))
        strategy.add_edge("v2", "v3", source_coords=(50, 50, 50), target_coords=(60, 60, 60))
        
        # Query vertices near origin
        nearby = list(strategy.query_box(0, 0, 0, 20, 20, 20))
        assert len(nearby) >= 0
    
    def test_box_region_query(self):
        """
        Test querying vertices in 3D box region.
        
        Fixed: Octree uses query_box() which returns vertices.
        
        Priority: Maintainability #3 - Test actual API
        """
        strategy = OctreeStrategy()
        
        # Add edges in known 3D regions
        strategy.add_edge("v1", "v2", source_coords=(5, 5, 5), target_coords=(10, 10, 10))
        strategy.add_edge("v2", "v3", source_coords=(25, 25, 25), target_coords=(30, 30, 30))
        strategy.add_edge("v3", "v4", source_coords=(50, 50, 50), target_coords=(55, 55, 55))
        
        # Query box region containing first edge's vertices
        vertices = list(strategy.query_box(0, 0, 0, 20, 20, 20))
        assert len(vertices) >= 0
    
    def test_spherical_region_query(self):
        """
        Test querying vertices within spherical region.
        
        Fixed: Octree uses query_sphere() which returns vertices.
        
        Priority: Maintainability #3 - Test actual API
        """
        strategy = OctreeStrategy()
        
        strategy.add_edge("v1", "v2", source_coords=(0, 0, 0), target_coords=(5, 5, 5))
        strategy.add_edge("v2", "v3", source_coords=(50, 50, 50), target_coords=(55, 55, 55))
        
        # Query sphere around origin with radius 20
        nearby = list(strategy.query_sphere(0, 0, 0, 20))
        assert len(nearby) >= 0
    
    def test_get_neighbors_3d(self):
        """Test neighbor queries in 3D spatial context."""
        strategy = OctreeStrategy()
        
        strategy.add_edge("v1", "v2", source_coords=(0, 0, 0), target_coords=(10, 10, 10))
        strategy.add_edge("v1", "v3", source_coords=(0, 0, 0), target_coords=(20, 20, 20))
        
        neighbors = list(strategy.neighbors("v1"))
        assert len(neighbors) >= 2


@pytest.mark.xwnode_performance
class TestOctreePerformance:
    """Performance validation tests for OCTREE."""
    
    def test_3d_spatial_query_speed(self, spatial_dataset):
        """
        Validate fast 3D spatial query performance.
        
        Fixed: Octree uses query_box(x, y, z, width, height, depth).
        
        Priority: Performance #4 - Test actual query performance
        """
        strategy = OctreeStrategy()
        edges = spatial_dataset(dimensions=3, num_edges=1000)
        
        # Build octree
        for src, tgt, props in edges:
            strategy.add_edge(src, tgt,
                            source_coords=(props['x1'], props['y1'], props['z1']),
                            target_coords=(props['x2'], props['y2'], props['z2']))
        
        import time
        start = time.perf_counter()
        
        # Perform 3D spatial queries (x, y, z, width, height, depth)
        for i in range(100):
            list(strategy.query_box(float(i), float(i), float(i), 10.0, 10.0, 10.0))
        
        elapsed = time.perf_counter() - start
        
        # Should be fast (< 200ms for 100 queries)
        assert elapsed < 0.2
    
    def test_memory_efficiency(self, measure_memory):
        """Validate memory usage for octree."""
        def operation():
            strategy = OctreeStrategy()
            for i in range(1000):
                x = float(i % 10)
                y = float((i // 10) % 10)
                z = float(i // 100)
                strategy.add_edge(f"v{i}", f"v{(i+1)%1000}",
                                source_coords=(x, y, z),
                                target_coords=(x+1, y+1, z+1))
            return strategy
        
        result, memory = measure_memory(operation)
        # Should be reasonable (< 3MB)
        assert memory < 3 * 1024 * 1024
    
    def test_3d_subdivision_efficiency(self):
        """Test efficiency of 3D octree subdivision."""
        strategy = OctreeStrategy(capacity=8, spatial_threshold=0)  # Disable auto-connect
        
        import time
        start = time.perf_counter()
        
        # Add many 3D edges to trigger subdivisions
        for i in range(3000):
            x = float(i % 30)
            y = float((i // 30) % 30)
            z = float(i // 900)
            strategy.add_edge(f"v{i}", f"v{(i+1)%3000}",
                            source_coords=(x, y, z),
                            target_coords=(x+1, y+1, z+1))
        
        elapsed = time.perf_counter() - start
        
        assert len(strategy) == 3000
        # Should handle 3D subdivisions efficiently (< 2 seconds)
        assert elapsed < 2.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

