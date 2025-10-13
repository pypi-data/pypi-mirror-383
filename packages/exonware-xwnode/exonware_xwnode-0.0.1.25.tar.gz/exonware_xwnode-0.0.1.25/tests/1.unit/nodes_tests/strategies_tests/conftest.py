"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/conftest.py

Node strategy test fixtures.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest


@pytest.fixture
def strategy_test_data():
    """Test data for strategy testing."""
    return {
        'simple': {'a': 1, 'b': 2},
        'complex': {f'key_{i}': f'value_{i}' for i in range(100)}
    }

