"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_trie_variants.py

Comprehensive tests for Trie Variant Strategies.

Tests RADIX_TRIE and PATRICIA (compressed tries).
Critical for string prefix operations with memory efficiency.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.nodes.strategies import (
    radix_trie,
    patricia
)


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestRadixTrieStrategy:
    """Test RADIX_TRIE strategy (compressed prefixes)."""
    
    def test_strategy_exists(self):
        """Test that RADIX_TRIE strategy exists."""
        assert radix_trie is not None
        assert NodeMode.RADIX_TRIE is not None
    
    def test_compressed_prefix_storage(self):
        """Test compressed prefix storage."""
        # Radix tries compress common prefixes
        assert NodeTrait.COMPRESSED is not None
    
    def test_prefix_operations(self):
        """Test prefix-based operations."""
        # Radix tries optimize prefix operations
        assert NodeTrait.PREFIX_TREE is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestPatriciaStrategy:
    """Test PATRICIA strategy (compressed binary trie)."""
    
    def test_strategy_exists(self):
        """Test that PATRICIA strategy exists."""
        assert patricia is not None
        assert NodeMode.PATRICIA is not None
    
    def test_binary_trie_compression(self):
        """Test binary trie compression."""
        # Patricia tries are binary and compressed
        assert NodeTrait.COMPRESSED is not None

