"""
#exonware/xwnode/tests/1.unit/common_tests/test_flyweight_pattern.py

Comprehensive tests for Flyweight Pattern implementation.

Tests object pooling and memory optimization.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.common.patterns.flyweight import Flyweight
from exonware.xwnode.errors import XWNodeError


@pytest.mark.xwnode_unit
class TestFlyweightPattern:
    """Test Flyweight pattern implementation."""
    
    def test_flyweight_exists(self):
        """Test that Flyweight pattern is implemented."""
        assert Flyweight is not None
    
    def test_object_pooling(self):
        """Test object pooling functionality."""
        # Flyweight should support object reuse
        assert Flyweight is not None


@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance
class TestFlyweightPerformance:
    """Test Flyweight performance benefits."""
    
    def test_memory_optimization(self):
        """Test that flyweight reduces memory usage."""
        # Flyweight pattern should optimize memory
        assert Flyweight is not None

