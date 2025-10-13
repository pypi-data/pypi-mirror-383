"""
Unit tests for TREE_GRAPH_BASIC edge strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.edges.strategies.tree_graph_basic import TreeGraphBasicStrategy
from exonware.xwnode.defs import EdgeMode, EdgeTrait


@pytest.mark.xwnode_core
class TestTreeGraphBasicCore:
    """Core tests for TREE_GRAPH_BASIC edge strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = TreeGraphBasicStrategy()
        assert strategy is not None
        assert strategy.mode == EdgeMode.TREE_GRAPH_BASIC
        assert len(strategy) == 0
    
    def test_tree_structure(self):
        """Test tree structure maintenance."""
        strategy = TreeGraphBasicStrategy()
        strategy.add_edge("root", "child1")
        strategy.add_edge("root", "child2")
        strategy.add_edge("child1", "grandchild1")
        
        assert len(strategy) == 3
    
    def test_parent_child_relationships(self):
        """Test parent-child navigation."""
        strategy = TreeGraphBasicStrategy()
        strategy.add_edge("parent", "child")
        
        children = list(strategy.get_children("parent"))
        assert "child" in children
    
    def test_supported_traits(self):
        """Test trait support."""
        strategy = TreeGraphBasicStrategy()
        traits = strategy.get_supported_traits()
        assert EdgeTrait.HIERARCHICAL in traits


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

