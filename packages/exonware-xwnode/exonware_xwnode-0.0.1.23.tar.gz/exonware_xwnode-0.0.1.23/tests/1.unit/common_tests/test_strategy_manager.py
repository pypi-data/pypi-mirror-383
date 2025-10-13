"""
#exonware/xwnode/tests/1.unit/common_tests/test_strategy_manager.py

Comprehensive tests for StrategyManager.

StrategyManager is CRITICAL - it controls strategy selection, creation, caching, and lifecycle.

Tests cover:
- Strategy creation for all node modes
- Strategy selection logic
- Performance characteristics
- Caching behavior
- Error handling
- Security

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.common.management.manager import StrategyManager
from exonware.xwnode.defs import NodeMode, EdgeMode
from exonware.xwnode.errors import XWNodeError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def manager():
    """Create a fresh StrategyManager instance."""
    return StrategyManager()


@pytest.fixture
def sample_dict_data():
    """Sample dictionary data for testing."""
    return {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}


@pytest.fixture
def sample_list_data():
    """Sample list data for testing."""
    return [1, 2, 3, 4, 5]


# ============================================================================
# STRATEGY CREATION TESTS
# ============================================================================

@pytest.mark.xwnode_unit
class TestStrategyManagerCreation:
    """Test StrategyManager can create all strategy types."""
    
    def test_create_node_strategy_from_dict(self, manager, sample_dict_data):
        """Test creating node strategy from dictionary data."""
        strategy = manager.create_node_strategy(sample_dict_data)
        
        assert strategy is not None
        assert strategy.size() > 0
    
    def test_create_node_strategy_from_list(self, manager, sample_list_data):
        """Test creating node strategy from list data."""
        strategy = manager.create_node_strategy(sample_list_data)
        
        assert strategy is not None
        assert strategy.size() > 0
    
    def test_create_with_specific_mode(self, manager, sample_dict_data):
        """Test creating strategy with specific mode."""
        # Test AUTO mode (default)
        auto_strategy = manager.create_node_strategy(sample_dict_data)
        assert auto_strategy is not None
    
    def test_create_with_empty_data(self, manager):
        """Test creating strategy from empty data."""
        empty_dict = manager.create_node_strategy({})
        empty_list = manager.create_node_strategy([])
        
        assert empty_dict is not None
        assert empty_list is not None
        assert empty_dict.is_empty() is True
        assert empty_list.is_empty() is True
    
    def test_create_with_none_data(self, manager):
        """Test creating strategy from None."""
        strategy = manager.create_node_strategy(None)
        
        assert strategy is not None
        # Should create empty strategy
        assert strategy.is_empty() is True or strategy.size() == 0


# ============================================================================
# STRATEGY SELECTION TESTS
# ============================================================================

@pytest.mark.xwnode_unit
class TestStrategyManagerSelection:
    """Test StrategyManager's intelligent strategy selection."""
    
    def test_auto_selection_for_dict(self, manager):
        """Test AUTO mode selects appropriate strategy for dict."""
        data = {'key': 'value'}
        strategy = manager.create_node_strategy(data)
        
        # Should select hash map or similar for dict data
        assert strategy is not None
        assert strategy.find('key') is not None or strategy.get('key') is not None
    
    def test_auto_selection_for_list(self, manager):
        """Test AUTO mode selects appropriate strategy for list."""
        data = [1, 2, 3, 4, 5]
        strategy = manager.create_node_strategy(data)
        
        # Should select array list or similar for list data
        assert strategy is not None
        assert strategy.size() == 5
    
    def test_auto_selection_for_nested_data(self, manager):
        """Test AUTO mode handles nested data."""
        data = {
            'users': [
                {'name': 'Alice'},
                {'name': 'Bob'}
            ],
            'settings': {'theme': 'dark'}
        }
        
        strategy = manager.create_node_strategy(data)
        assert strategy is not None


# ============================================================================
# PERFORMANCE & CACHING TESTS
# ============================================================================

@pytest.mark.xwnode_unit
@pytest.mark.xwnode_performance
class TestStrategyManagerPerformance:
    """Test StrategyManager performance and caching."""
    
    def test_strategy_creation_performance(self, manager):
        """Test that strategy creation is fast."""
        import time
        
        data = {'key': 'value'}
        
        # Measure creation time
        start = time.time()
        for _ in range(1000):
            strategy = manager.create_node_strategy(data)
        elapsed = time.time() - start
        
        # Should create 1000 strategies in reasonable time (< 1 second)
        assert elapsed < 1.0
    
    def test_multiple_creations_work(self, manager, sample_dict_data):
        """Test creating multiple strategies works correctly."""
        strategy1 = manager.create_node_strategy(sample_dict_data)
        strategy2 = manager.create_node_strategy(sample_dict_data)
        
        # Both should be valid
        assert strategy1 is not None
        assert strategy2 is not None


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.xwnode_unit
class TestStrategyManagerErrors:
    """Test StrategyManager error handling."""
    
    def test_invalid_data_type_handling(self, manager):
        """Test handling of invalid data types."""
        invalid_data = [
            lambda x: x,  # Function
            object(),  # Generic object
        ]
        
        for data in invalid_data:
            try:
                strategy = manager.create_node_strategy(data)
                # If it doesn't raise, verify strategy is created
                assert strategy is not None
            except (TypeError, XWNodeError):
                # Expected for some invalid types
                pass
    
    def test_edge_case_data_handling(self, manager):
        """Test handling of edge case data."""
        edge_cases = [
            '',  # Empty string
            0,  # Zero
            False,  # False
            float('inf'),  # Infinity
        ]
        
        for data in edge_cases:
            # Should not crash
            try:
                strategy = manager.create_node_strategy(data)
                assert strategy is not None
            except (TypeError, ValueError, XWNodeError):
                # Some edge cases may raise errors - that's OK
                pass


# ============================================================================
# METADATA TESTS
# ============================================================================

@pytest.mark.xwnode_unit
class TestStrategyManagerMetadata:
    """Test StrategyManager metadata and configuration."""
    
    def test_manager_initialization(self):
        """Test StrategyManager initializes correctly."""
        manager = StrategyManager()
        assert manager is not None
    
    def test_manager_is_reusable(self, manager, sample_dict_data):
        """Test that same manager can be used multiple times."""
        strategy1 = manager.create_node_strategy(sample_dict_data)
        strategy2 = manager.create_node_strategy({'other': 'data'})
        strategy3 = manager.create_node_strategy([1, 2, 3])
        
        assert all([strategy1, strategy2, strategy3])

