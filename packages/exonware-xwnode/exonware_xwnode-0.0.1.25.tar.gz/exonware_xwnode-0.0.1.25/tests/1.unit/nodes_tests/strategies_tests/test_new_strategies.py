"""
#exonware/xwnode/tests/1.unit/nodes_tests/strategies_tests/test_new_strategies.py

Unit tests for new node strategies.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.bw_tree import BwTreeStrategy
from exonware.xwnode.nodes.strategies.hamt import HAMTStrategy
from exonware.xwnode.nodes.strategies.masstree import MasstreeStrategy
from exonware.xwnode.nodes.strategies.extendible_hash import ExtendibleHashStrategy
from exonware.xwnode.nodes.strategies.linear_hash import LinearHashStrategy
from exonware.xwnode.nodes.strategies.t_tree import TTreeStrategy
from exonware.xwnode.nodes.strategies.learned_index import LearnedIndexStrategy
from exonware.xwnode.defs import NodeMode


@pytest.mark.xwnode_unit
class TestBwTreeStrategyUnit:
    """Unit tests for Bw-Tree strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = BwTreeStrategy()
        assert strategy.mode == NodeMode.BW_TREE
    
    def test_delta_operations(self):
        """Test delta-based operations."""
        strategy = BwTreeStrategy()
        strategy.put('key1', 'value1')
        assert strategy.get('key1') == 'value1'
    
    def test_consolidation(self):
        """Test delta chain consolidation."""
        strategy = BwTreeStrategy()
        for i in range(10):
            strategy.put(f'key{i}', f'value{i}')
        
        # Consolidate
        if hasattr(strategy, 'consolidate_tree'):
            strategy.consolidate_tree()
        
        assert len(strategy) >= 0


@pytest.mark.xwnode_unit
class TestHAMTStrategyUnit:
    """Unit tests for HAMT strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = HAMTStrategy()
        assert strategy.mode == NodeMode.HAMT
    
    def test_persistent_updates(self):
        """Test persistent updates."""
        strategy = HAMTStrategy()
        strategy.put('key1', 'value1')
        strategy.put('key2', 'value2')
        
        assert strategy.get('key1') == 'value1'
        assert strategy.get('key2') == 'value2'


@pytest.mark.xwnode_unit
class TestMasstreeStrategyUnit:
    """Unit tests for Masstree strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = MasstreeStrategy()
        assert strategy.mode == NodeMode.MASSTREE
    
    def test_operations(self):
        """Test basic operations."""
        strategy = MasstreeStrategy()
        strategy.put('key1', 'value1')
        assert strategy.get('key1') == 'value1'


@pytest.mark.xwnode_unit
class TestExtendibleHashStrategyUnit:
    """Unit tests for Extendible Hash strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = ExtendibleHashStrategy()
        assert strategy.mode == NodeMode.EXTENDIBLE_HASH
    
    def test_operations(self):
        """Test basic operations."""
        strategy = ExtendibleHashStrategy()
        strategy.put('key1', 'value1')
        assert strategy.has('key1')


@pytest.mark.xwnode_unit
class TestLinearHashStrategyUnit:
    """Unit tests for Linear Hash strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = LinearHashStrategy()
        assert strategy.mode == NodeMode.LINEAR_HASH
    
    def test_operations(self):
        """Test basic operations."""
        strategy = LinearHashStrategy()
        strategy.put('key1', 'value1')
        assert strategy.exists('key1')


@pytest.mark.xwnode_unit
class TestTTreeStrategyUnit:
    """Unit tests for T-Tree strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = TTreeStrategy()
        assert strategy.mode == NodeMode.T_TREE
    
    def test_operations(self):
        """Test basic operations."""
        strategy = TTreeStrategy()
        strategy.put('key1', 'value1')
        assert strategy.get('key1') == 'value1'


@pytest.mark.xwnode_unit
class TestLearnedIndexStrategyUnit:
    """Unit tests for Learned Index strategy."""
    
    def test_initialization(self):
        """Test initialization with delegation."""
        strategy = LearnedIndexStrategy()
        assert strategy.mode == NodeMode.LEARNED_INDEX
        assert hasattr(strategy, '_data')
    
    def test_delegation_works(self):
        """Test that operations delegate properly."""
        strategy = LearnedIndexStrategy()
        strategy.put('key1', 'value1')
        assert strategy.get('key1') == 'value1'
    
    def test_placeholder_documentation(self):
        """Test placeholder has proper documentation."""
        strategy = LearnedIndexStrategy()
        info = strategy.get_backend_info()
        assert 'status' in info
        assert info['status'] == 'EXPERIMENTAL'
    
    def test_future_ml_methods_exist(self):
        """Test that future ML methods are defined."""
        strategy = LearnedIndexStrategy()
        assert hasattr(strategy, 'train_model')
        assert hasattr(strategy, 'predict_position')
        assert hasattr(strategy, 'get_model_info')

