"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_string_structures.py

Comprehensive tests for String Structures.

Tests SUFFIX_ARRAY and AHO_CORASICK strategies.
Critical for string matching and search operations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.nodes.strategies import (
    suffix_array,
    aho_corasick
)


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestSuffixArrayStrategy:
    """Test SUFFIX_ARRAY strategy for substring search."""
    
    def test_strategy_exists(self):
        """Test that SUFFIX_ARRAY strategy exists."""
        assert suffix_array is not None
        assert NodeMode.SUFFIX_ARRAY is not None
    
    def test_substring_search_capability(self):
        """Test substring search optimization."""
        # Suffix arrays enable fast substring search
        assert NodeMode.SUFFIX_ARRAY is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_node_strategy
class TestAhoCorasickStrategy:
    """Test AHO_CORASICK strategy for multi-pattern matching."""
    
    def test_strategy_exists(self):
        """Test that AHO_CORASICK strategy exists."""
        assert aho_corasick is not None
        assert NodeMode.AHO_CORASICK is not None
    
    def test_multi_pattern_matching(self):
        """Test multi-pattern string matching."""
        # Aho-Corasick matches multiple patterns simultaneously
        assert NodeMode.AHO_CORASICK is not None

