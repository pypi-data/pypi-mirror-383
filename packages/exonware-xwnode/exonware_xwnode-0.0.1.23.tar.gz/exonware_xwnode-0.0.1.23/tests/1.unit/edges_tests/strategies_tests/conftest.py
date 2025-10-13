"""
#exonware/xwnode/tests/1.unit/edges_tests/strategies_tests/conftest.py

Edge strategy test fixtures.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest


@pytest.fixture
def edge_strategy_test_data():
    """Test data for edge strategy testing."""
    return {
        'adjacency_list': {0: [1, 2], 1: [2], 2: [3], 3: []},
        'adjacency_matrix': [[0, 1, 1, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0]]
    }

