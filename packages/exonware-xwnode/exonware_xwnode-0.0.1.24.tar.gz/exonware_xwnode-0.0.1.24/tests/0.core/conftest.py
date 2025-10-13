"""
#exonware/xwnode/tests/0.core/conftest.py

Core test fixtures - Minimal setup, no external services.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from pathlib import Path


@pytest.fixture
def core_test_data():
    """Fast, minimal test data for core tests."""
    return {
        'key1': 'value1',
        'key2': 'value2',
        'nested': {
            'inner': 'value'
        }
    }


@pytest.fixture
def core_data_dir():
    """Get the core test data directory."""
    return Path(__file__).parent / "data"
