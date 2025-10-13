"""
#exonware/xwnode/tests/1.unit/common_tests/test_utils.py

Comprehensive tests for common utilities.

Tests helper functions and utility classes.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.common.utils.utils import *
from exonware.xwnode.common.utils.simple import SimpleNodeStrategy


@pytest.mark.xwnode_unit
class TestSimpleNodeStrategy:
    """Test SimpleNodeStrategy fallback."""
    
    def test_simple_strategy_creation(self):
        """Test creating simple strategy."""
        data = {'key': 'value'}
        strategy = SimpleNodeStrategy.create_from_data(data)
        
        assert strategy is not None
    
    def test_simple_strategy_operations(self):
        """Test basic operations on simple strategy."""
        strategy = SimpleNodeStrategy.create_from_data({'key': 'value'})
        
        # Should support basic operations
        assert strategy.to_native() is not None


@pytest.mark.xwnode_unit
class TestUtils:
    """Test utility functions."""
    
    def test_utils_module_exists(self):
        """Test that utils module exists and is importable."""
        from exonware.xwnode.common.utils import utils
        assert utils is not None

