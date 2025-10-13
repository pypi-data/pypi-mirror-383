"""
#exonware/xwnode/tests/1.unit/common_tests/conftest.py

Common module test fixtures.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest


@pytest.fixture
def common_test_data():
    """Test data for common module testing."""
    return {
        'registry': {'strategy1': 'impl1', 'strategy2': 'impl2'},
        'manager': {'config': {'setting': 'value'}}
    }

