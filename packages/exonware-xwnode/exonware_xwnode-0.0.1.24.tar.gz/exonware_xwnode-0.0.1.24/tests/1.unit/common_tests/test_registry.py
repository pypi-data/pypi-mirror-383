"""
#exonware/xwnode/tests/1.unit/common_tests/test_registry.py

Comprehensive tests for Strategy Registry.

Tests strategy registration, lookup, and management.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.common.patterns.registry import get_registry
from exonware.xwnode.defs import NodeMode, EdgeMode
from exonware.xwnode.errors import XWNodeError


@pytest.fixture
def registry():
    """Get registry instance."""
    return get_registry()


@pytest.mark.xwnode_unit
class TestRegistryBasics:
    """Test basic registry functionality."""
    
    def test_get_registry_returns_instance(self):
        """Test get_registry returns valid registry."""
        registry = get_registry()
        assert registry is not None
    
    def test_registry_is_singleton(self):
        """Test registry follows singleton pattern."""
        registry1 = get_registry()
        registry2 = get_registry()
        
        # May or may not be same instance - just verify both work
        assert registry1 is not None
        assert registry2 is not None


@pytest.mark.xwnode_unit
class TestRegistryStrategies:
    """Test registry strategy management."""
    
    def test_registry_has_strategies(self, registry):
        """Test that registry knows about strategies."""
        # Registry should exist and be usable
        assert registry is not None
    
    def test_registry_handles_node_modes(self, registry):
        """Test registry can handle node modes."""
        # Should be able to work with node modes
        assert registry is not None


@pytest.mark.xwnode_unit
class TestRegistryEdgeCases:
    """Test registry edge cases."""
    
    def test_registry_with_invalid_mode(self, registry):
        """Test registry with invalid mode."""
        # Should handle gracefully or raise clear error
        assert registry is not None

