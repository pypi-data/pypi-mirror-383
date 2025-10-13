"""
#exonware/xwnode/tests/1.unit/edges_tests/conftest.py

Edge module test fixtures.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest


@pytest.fixture
def edge_test_data():
    """Test data specific to edge testing."""
    return {
        'simple_graph': {
            'edges': [(0, 1), (1, 2), (2, 3)],
            'vertices': [0, 1, 2, 3]
        },
        'weighted_graph': {
            'edges': [(0, 1, 5), (1, 2, 3), (2, 3, 7)],
            'vertices': [0, 1, 2, 3]
        }
    }

