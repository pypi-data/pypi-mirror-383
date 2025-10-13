"""
#exonware/xwnode/tests/1.unit/nodes_tests/conftest.py

Node module test fixtures.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest


@pytest.fixture
def node_test_data():
    """Test data specific to node testing."""
    return {
        'hash_map_data': {'key1': 'value1', 'key2': 'value2'},
        'tree_data': {'root': {'left': 'a', 'right': 'b'}},
        'list_data': [1, 2, 3, 4, 5]
    }

