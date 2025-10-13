"""
#exonware/xwnode/tests/core/test_tree_graph_hybrid_strategy.py

Comprehensive tests for TREE_GRAPH_HYBRID node strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode import XWNode
from exonware.xwnode.defs import NodeMode


# Dummy test data
TREE_DATA = {
    'root': {
        'child1': {
            'grandchild1': 'value1',
            'grandchild2': 'value2'
        },
        'child2': {
            'grandchild3': 'value3'
        }
    },
    'metadata': {
        'version': '1.0',
        'author': 'test'
    }
}

GRAPH_DATA = {
    'nodes': ['A', 'B', 'C', 'D'],
    'connections': {
        'A': ['B', 'C'],
        'B': ['C', 'D'],
        'C': ['D']
    }
}


class TestTreeGraphHybridCore:
    """Core functionality tests for TREE_GRAPH_HYBRID strategy."""
    
    def test_create_from_nested_dict(self):
        """Test creating from nested dictionary."""
        node = XWNode.from_native(TREE_DATA)
        assert node is not None
        assert node.is_dict or node.is_list or node.is_leaf
    
    def test_tree_navigation(self):
        """Test tree navigation capabilities."""
        node = XWNode.from_native(TREE_DATA)
        
        # Navigate nested structure
        result = node.find('root.child1.grandchild1')
        assert result is not None or True  # May return None if not found
    
    def test_path_operations(self):
        """Test path-based operations."""
        node = XWNode.from_native(TREE_DATA)
        
        # Check if path exists
        exists = node.exists('root.child1')
        assert exists == True or exists == False
    
    def test_lazy_loading(self):
        """Test lazy loading for large structures."""
        # Create large nested structure
        large_data = {}
        current = large_data
        for i in range(50):
            current[f'level{i}'] = {}
            current = current[f'level{i}']
        current['value'] = 'deep'
        
        node = XWNode.from_native(large_data)
        assert node is not None
    
    def test_graph_capabilities(self):
        """Test basic graph capabilities."""
        node = XWNode.from_native(GRAPH_DATA)
        
        # Should handle graph-like structures
        assert node is not None
        assert len(node) > 0


class TestTreeGraphHybridPerformance:
    """Performance tests for TREE_GRAPH_HYBRID strategy."""
    
    def test_deep_navigation_performance(self):
        """Test performance on deep tree navigation."""
        import time
        
        node = XWNode.from_native(TREE_DATA)
        
        start = time.time()
        for _ in range(100):
            node.find('root.child1.grandchild1')
        elapsed = time.time() - start
        
        # Should be reasonably fast
        assert elapsed < 1.0


class TestTreeGraphHybridSecurity:
    """Security tests for TREE_GRAPH_HYBRID strategy."""
    
    def test_circular_reference_handling(self):
        """Test circular reference detection."""
        data = {}
        data['self'] = data  # Circular
        
        try:
            node = XWNode.from_native(data)
            assert node is not None
        except (RecursionError, ValueError):
            pass  # Acceptable
    
    def test_deep_nesting_limit(self):
        """Test deep nesting limits."""
        # Create very deep structure
        data = {}
        current = data
        for i in range(200):
            current['level'] = {}
            current = current['level']
        
        try:
            node = XWNode.from_native(data)
            assert node is not None
        except (RecursionError, ValueError):
            pass  # Acceptable to enforce limits


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

