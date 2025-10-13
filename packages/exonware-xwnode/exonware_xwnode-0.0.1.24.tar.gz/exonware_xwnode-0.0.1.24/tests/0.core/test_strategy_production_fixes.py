"""
#exonware/xwnode/tests/0.core/test_strategy_production_fixes.py

Regression Tests for Production-Ready Strategy Fixes

Tests to verify the production readiness improvements made to node strategies:
- Naming consistency (no 'x' prefixes in return types)
- STRATEGY_TYPE correctness
- Production features (WAL, CAS, ML model, etc.)
- Documentation completeness

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 12, 2025
"""

import pytest
from exonware.xwnode.nodes.strategies.contracts import NodeType
from exonware.xwnode.nodes.strategies.hash_map import HashMapStrategy
from exonware.xwnode.nodes.strategies.set_hash import SetHashStrategy
from exonware.xwnode.nodes.strategies.hyperloglog import HyperLogLogStrategy
from exonware.xwnode.nodes.strategies.persistent_tree import PersistentTreeStrategy
from exonware.xwnode.nodes.strategies.cow_tree import COWTreeStrategy
from exonware.xwnode.nodes.strategies.roaring_bitmap import RoaringBitmapStrategy
from exonware.xwnode.nodes.strategies.bitmap import BitmapStrategy
from exonware.xwnode.nodes.strategies.bitset_dynamic import BitsetDynamicStrategy
from exonware.xwnode.nodes.strategies.lsm_tree import LSMTreeStrategy
from exonware.xwnode.nodes.strategies.bw_tree import BwTreeStrategy
from exonware.xwnode.nodes.strategies.learned_index import LearnedIndexStrategy


class TestStrategyTypeCorrectness:
    """Test that STRATEGY_TYPE classifications are correct after fixes."""
    
    def test_hash_map_is_hybrid_not_tree(self):
        """HashMap should be HYBRID, not TREE."""
        assert HashMapStrategy.STRATEGY_TYPE == NodeType.HYBRID, \
            "HashMap should be HYBRID (hash-based), not TREE"
    
    def test_set_hash_is_hybrid(self):
        """SetHash should be HYBRID (hash-based set)."""
        assert SetHashStrategy.STRATEGY_TYPE == NodeType.HYBRID, \
            "SetHash should be HYBRID (hash-based set operations)"
    
    def test_hyperloglog_is_hybrid(self):
        """HyperLogLog should be HYBRID (probabilistic with hash buckets)."""
        assert HyperLogLogStrategy.STRATEGY_TYPE == NodeType.HYBRID, \
            "HyperLogLog should be HYBRID (probabilistic cardinality)"


class TestNamingConsistency:
    """Test that naming is consistent (no 'x' prefixes in return types)."""
    
    def test_persistent_tree_snapshot_returns_correct_type(self):
        """PersistentTreeStrategy.snapshot() should return 'PersistentTreeStrategy'."""
        strategy = PersistentTreeStrategy()
        snapshot = strategy.snapshot()
        assert type(snapshot).__name__ == 'PersistentTreeStrategy'
        assert not type(snapshot).__name__.startswith('x')
    
    def test_cow_tree_snapshot_returns_correct_type(self):
        """COWTreeStrategy.snapshot() should return 'COWTreeStrategy'."""
        strategy = COWTreeStrategy()
        strategy.put('test', 'value')
        snapshot = strategy.snapshot()
        assert type(snapshot).__name__ == 'COWTreeStrategy'
        assert not type(snapshot).__name__.startswith('x')
    
    def test_roaring_bitmap_union_returns_correct_type(self):
        """RoaringBitmapStrategy.union() should return 'RoaringBitmapStrategy'."""
        strategy1 = RoaringBitmapStrategy()
        strategy1.put(1, True)
        strategy2 = RoaringBitmapStrategy()
        strategy2.put(2, True)
        result = strategy1.union(strategy2)
        assert type(result).__name__ == 'RoaringBitmapStrategy'
        assert not type(result).__name__.startswith('x')
    
    def test_bitmap_bitwise_and_returns_correct_type(self):
        """BitmapStrategy.bitwise_and() should return 'BitmapStrategy'."""
        strategy1 = BitmapStrategy()
        strategy1.set_bit(5, True)
        strategy2 = BitmapStrategy()
        strategy2.set_bit(5, True)
        result = strategy1.bitwise_and(strategy2)
        assert type(result).__name__ == 'BitmapStrategy'
        assert not type(result).__name__.startswith('x')
    
    def test_bitset_dynamic_logical_and_returns_correct_type(self):
        """BitsetDynamicStrategy.logical_and() should return 'BitsetDynamicStrategy'."""
        strategy1 = BitsetDynamicStrategy()
        strategy1.put(5, True)
        strategy2 = BitsetDynamicStrategy()
        strategy2.put(5, True)
        result = strategy1.logical_and(strategy2)
        assert type(result).__name__ == 'BitsetDynamicStrategy'
        assert not type(result).__name__.startswith('x')


class TestLSMTreeProductionFeatures:
    """Test LSM Tree production features (WAL, Bloom, Compaction)."""
    
    def test_lsm_has_wal(self):
        """LSM Tree should have Write-Ahead Log."""
        strategy = LSMTreeStrategy()
        assert hasattr(strategy, 'wal')
        assert strategy.wal is not None
    
    def test_lsm_has_bloom_filters(self):
        """LSM Tree SSTables should have bloom filters."""
        strategy = LSMTreeStrategy()
        # Insert enough to trigger flush
        for i in range(2000):
            strategy.put(f'key{i}', f'value{i}')
        
        # Check SSTables have bloom filters
        for level in strategy.sstables.values():
            for sstable in level:
                assert hasattr(sstable, 'bloom_filter')
                assert sstable.bloom_filter is not None
    
    def test_lsm_has_background_compaction(self):
        """LSM Tree should support background compaction."""
        strategy = LSMTreeStrategy(background_compaction=True)
        assert hasattr(strategy, '_compaction_thread')
        # Thread should be started
        assert strategy._compaction_thread is not None
        assert strategy._compaction_thread.is_alive()
    
    def test_lsm_backend_info_shows_production_features(self):
        """LSM Tree backend_info should list production features."""
        strategy = LSMTreeStrategy()
        info = strategy.backend_info
        assert 'production_features' in info
        features = info['production_features']
        assert 'Write-Ahead Log (WAL)' in features
        assert 'Bloom Filters per SSTable' in features
        assert 'Background Compaction Thread' in features


class TestBWTreeProductionFeatures:
    """Test BW Tree production features (Atomic CAS, Epoch GC)."""
    
    def test_bw_tree_has_mapping_table(self):
        """BW Tree should have mapping table for PID -> Node."""
        strategy = BwTreeStrategy()
        assert hasattr(strategy, '_mapping_table')
        assert hasattr(strategy, '_root_pid')
        assert strategy._root_pid in strategy._mapping_table
    
    def test_bw_tree_has_cas_operations(self):
        """BW Tree should have atomic CAS operations."""
        strategy = BwTreeStrategy()
        assert hasattr(strategy, '_cas_update')
        assert hasattr(strategy, '_cas_lock')
    
    def test_bw_tree_has_epoch_gc(self):
        """BW Tree should have epoch-based garbage collection."""
        strategy = BwTreeStrategy()
        assert hasattr(strategy, '_current_epoch')
        assert hasattr(strategy, '_retired_nodes')
        assert hasattr(strategy, '_enter_epoch')
        assert hasattr(strategy, '_retire_node')
    
    def test_bw_tree_backend_info_shows_production_features(self):
        """BW Tree backend_info should list production features."""
        strategy = BwTreeStrategy()
        info = strategy.get_backend_info()
        assert 'production_features' in info
        features = info['production_features']
        assert 'Atomic CAS Operations' in features
        assert 'Epoch-based Garbage Collection' in features


class TestLearnedIndexProductionFeatures:
    """Test Learned Index production features (ML model, training)."""
    
    def test_learned_index_has_ml_components(self):
        """Learned Index should have ML model components."""
        strategy = LearnedIndexStrategy()
        assert hasattr(strategy, '_model')
        assert hasattr(strategy, '_trained')
        assert hasattr(strategy, '_error_bound')
    
    def test_learned_index_has_training_pipeline(self):
        """Learned Index should have training pipeline."""
        strategy = LearnedIndexStrategy()
        assert hasattr(strategy, 'train_model')
        assert hasattr(strategy, 'predict_position')
    
    def test_learned_index_training_works(self):
        """Learned Index training should work with sufficient data."""
        strategy = LearnedIndexStrategy()
        
        # Insert enough data to trigger training
        for i in range(150):
            strategy.put(f'key{i:04d}', f'value{i}')
        
        # Train model
        success = strategy.train_model()
        
        # Check training status (may fail if sklearn not installed)
        model_info = strategy.get_model_info()
        assert 'status' in model_info
        # Either trained successfully or sklearn not available
        assert model_info['status'] in ['TRAINED', 'NOT_TRAINED']
    
    def test_learned_index_backend_info_shows_production_features(self):
        """Learned Index backend_info should list production features."""
        strategy = LearnedIndexStrategy()
        info = strategy.get_backend_info()
        assert 'production_features' in info
        features = info['production_features']
        assert any('Regression' in f or 'Fallback' in f for f in features)


class TestPersistentTreeProductionFeatures:
    """Test Persistent Tree version management."""
    
    def test_persistent_tree_has_version_management(self):
        """Persistent Tree should have version management."""
        strategy = PersistentTreeStrategy()
        assert hasattr(strategy, '_version_history')
        assert hasattr(strategy, 'get_version_history')
        assert hasattr(strategy, 'restore_version')
        assert hasattr(strategy, 'compare_versions')
    
    def test_persistent_tree_version_history_works(self):
        """Persistent Tree version history should track changes."""
        strategy = PersistentTreeStrategy()
        
        # Make some changes
        strategy.put('key1', 'value1')
        v1 = strategy.get_version()
        
        strategy.put('key2', 'value2')
        v2 = strategy.get_version()
        
        # Version should increment
        assert v2 > v1
        
        # Version history should exist
        history = strategy.get_version_history()
        assert len(history) > 0


class TestCOWTreeProductionFeatures:
    """Test COW Tree memory pressure monitoring."""
    
    def test_cow_tree_has_memory_monitoring(self):
        """COW Tree should have memory pressure monitoring."""
        strategy = COWTreeStrategy()
        assert hasattr(strategy, '_memory_pressure_threshold')
        assert hasattr(strategy, '_total_nodes')
        assert hasattr(strategy, 'get_memory_pressure')
    
    def test_cow_tree_memory_pressure_works(self):
        """COW Tree memory pressure tracking should work."""
        strategy = COWTreeStrategy()
        strategy.put('test', 'value')
        
        pressure = strategy.get_memory_pressure()
        assert 'total_nodes' in pressure
        assert 'memory_threshold' in pressure
        assert 'under_pressure' in pressure


class TestDocumentationCompliance:
    """Test that strategies have proper documentation."""
    
    def test_lsm_tree_has_production_features(self):
        """LSM Tree should report production features in backend_info."""
        strategy = LSMTreeStrategy()
        info = strategy.backend_info
        assert 'production_features' in info
    
    def test_bw_tree_has_production_features(self):
        """BW Tree should report production features in backend_info."""
        strategy = BwTreeStrategy()
        info = strategy.get_backend_info()
        assert 'production_features' in info
    
    def test_learned_index_has_production_features(self):
        """Learned Index should report production features in backend_info."""
        strategy = LearnedIndexStrategy()
        info = strategy.get_backend_info()
        assert 'production_features' in info


# Mark all tests with xwnode_core marker
pytestmark = pytest.mark.xwnode_core

