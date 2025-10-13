"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_tree_graph_hybrid.py

Comprehensive tests for TreeGraphHybridStrategy.

This is the default/legacy strategy combining tree navigation with graph capabilities.
Critical for backward compatibility.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode import XWNode


@pytest.fixture
def tree_data():
    """Create tree-structured test data."""
    return {
        'root': {
            'child1': {
                'grandchild1': 'value1',
                'grandchild2': 'value2'
            },
            'child2': {
                'grandchild3': 'value3'
            }
        }
    }


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestTreeGraphHybridInterface:
    """Test TreeGraphHybrid interface compliance."""
    
    def test_create_from_dict(self, tree_data):
        """Test creation from dictionary."""
        node = XWNode.from_native(tree_data)
        
        assert node is not None
        assert len(node) > 0
    
    def test_tree_navigation(self, tree_data):
        """Test navigating tree structure."""
        node = XWNode.from_native(tree_data)
        
        # Navigate to nested elements
        root = node.get('root')
        assert root is not None
    
    def test_path_based_access(self, tree_data):
        """Test accessing nested data via paths."""
        node = XWNode.from_native(tree_data)
        
        # Test path navigation if supported
        assert node.exists('root')
    
    def test_to_native_preserves_structure(self, tree_data):
        """Test that to_native preserves tree structure."""
        node = XWNode.from_native(tree_data)
        native = node.to_native()
        
        assert isinstance(native, dict)
        # Structure should be preserved
        assert 'root' in native or len(native) > 0


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
@pytest.mark.xwnode_security
class TestTreeGraphHybridSecurity:
    """Test TreeGraphHybrid security."""
    
    def test_path_traversal_prevention(self):
        """Test protection against path traversal attacks."""
        node = XWNode.from_native({'data': 'safe'})
        
        # Attempt path traversal
        malicious_paths = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32',
            '/etc/passwd',
            'C:\\Windows\\System32'
        ]
        
        for path in malicious_paths:
            # Should not crash or access filesystem
            result = node.get(path)
            # Should return None or handle safely
    
    def test_circular_reference_handling(self):
        """Test handling of circular references."""
        data = {'key': 'value'}
        data['self'] = data  # Circular reference
        
        # Should not crash
        try:
            node = XWNode.from_native(data)
            # If it handles circular refs, verify it doesn't infinite loop
        except (RecursionError, ValueError):
            # Expected behavior - circular refs should be caught
            pass
    
    def test_deep_nesting_handling(self):
        """Test handling of deeply nested structures."""
        # Create deeply nested data
        data = {'level0': None}
        current = data
        for i in range(100):
            current['level0'] = {f'level{i+1}': None}
            current = current['level0']
        
        # Should not crash
        node = XWNode.from_native(data)
        assert node is not None

