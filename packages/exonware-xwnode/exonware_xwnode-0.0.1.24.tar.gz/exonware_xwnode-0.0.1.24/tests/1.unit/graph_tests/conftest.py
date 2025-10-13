"""
#exonware/xwnode/tests/1.unit/graph_tests/conftest.py

Fixtures for graph manager unit tests.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.common.graph import XWGraphManager
from exonware.xwnode.defs import EdgeMode


@pytest.fixture
def graph_manager():
    """Create a basic graph manager for testing."""
    return XWGraphManager(
        edge_mode=EdgeMode.TREE_GRAPH_BASIC,
        enable_caching=True,
        enable_indexing=True
    )


@pytest.fixture
def graph_manager_no_cache():
    """Create graph manager without caching."""
    return XWGraphManager(
        edge_mode=EdgeMode.TREE_GRAPH_BASIC,
        enable_caching=False,
        enable_indexing=True
    )


@pytest.fixture
def graph_manager_no_index():
    """Create graph manager without indexing."""
    return XWGraphManager(
        edge_mode=EdgeMode.TREE_GRAPH_BASIC,
        enable_caching=True,
        enable_indexing=False
    )


@pytest.fixture
def sample_relationships():
    """Sample relationships for testing."""
    return [
        {'source': 'alice', 'target': 'bob', 'type': 'follows'},
        {'source': 'alice', 'target': 'charlie', 'type': 'follows'},
        {'source': 'bob', 'target': 'charlie', 'type': 'follows'},
        {'source': 'charlie', 'target': 'alice', 'type': 'follows'},
        {'source': 'alice', 'target': 'bob', 'type': 'likes'},
    ]

