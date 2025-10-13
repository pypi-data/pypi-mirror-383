"""
#exonware/xwnode/tests/1.unit/conftest.py

Unit test fixtures - Fakes/mocks only, no network/disk.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest


@pytest.fixture
def mock_strategy():
    """Mock strategy for testing."""
    class MockStrategy:
        def __init__(self, data=None):
            self._data = data or {}
        
        def to_native(self):
            return self._data
        
        def size(self):
            return len(self._data) if isinstance(self._data, (dict, list)) else 1
        
        def is_empty(self):
            return not self._data
        
        def insert(self, key, value):
            if isinstance(self._data, dict):
                self._data[key] = value
        
        def find(self, key):
            if isinstance(self._data, dict):
                return self._data.get(key)
            return None
        
        def delete(self, key):
            if isinstance(self._data, dict) and key in self._data:
                del self._data[key]
                return True
            return False
    
    return MockStrategy

