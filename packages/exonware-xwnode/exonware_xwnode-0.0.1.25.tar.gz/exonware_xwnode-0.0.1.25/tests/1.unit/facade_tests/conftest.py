"""
#exonware/xwnode/tests/1.unit/facade_tests/conftest.py

Facade module test fixtures.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest


@pytest.fixture
def facade_test_data():
    """Test data for facade testing."""
    return {
        'simple': {'key': 'value'},
        'complex': {'nested': {'deep': 'value'}}
    }

