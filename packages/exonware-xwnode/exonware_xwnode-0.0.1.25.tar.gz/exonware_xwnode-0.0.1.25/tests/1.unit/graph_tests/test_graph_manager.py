"""
#exonware/xwnode/tests/1.unit/graph_tests/test_graph_manager.py

Unit tests for XWGraphManager.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.common.graph import XWGraphManager, XWGraphSecurityError
from exonware.xwnode.defs import EdgeMode


@pytest.mark.xwnode_unit
class TestGraphManagerBasic:
    """Basic graph manager functionality tests."""
    
    def test_initialization(self, graph_manager):
        """Test graph manager initializes correctly."""
        assert graph_manager is not None
        assert graph_manager.edge_mode == EdgeMode.TREE_GRAPH_BASIC
        assert graph_manager.isolation_key is None
    
    def test_add_single_relationship(self, graph_manager):
        """Test adding a single relationship."""
        rel_id = graph_manager.add_relationship('alice', 'bob', 'follows')
        
        assert rel_id is not None
        assert isinstance(rel_id, str)
        
        # Verify it can be queried
        outgoing = graph_manager.get_outgoing('alice', 'follows')
        assert len(outgoing) == 1
    
    def test_add_multiple_relationships(self, graph_manager, sample_relationships):
        """Test adding multiple relationships."""
        for rel in sample_relationships:
            graph_manager.add_relationship(rel['source'], rel['target'], rel['type'])
        
        # Verify all were added
        stats = graph_manager.get_stats()
        assert stats['total_relationships'] == len(sample_relationships)
    
    def test_query_with_type_filter(self, graph_manager):
        """Test querying with relationship type filter."""
        # Add different types
        graph_manager.add_relationship('alice', 'bob', 'follows')
        graph_manager.add_relationship('alice', 'charlie', 'likes')
        
        # Query with filter
        follows = graph_manager.get_outgoing('alice', 'follows')
        likes = graph_manager.get_outgoing('alice', 'likes')
        
        assert len(follows) == 1
        assert len(likes) == 1
        assert follows[0]['type'] == 'follows'
        assert likes[0]['type'] == 'likes'
    
    def test_query_without_type_filter(self, graph_manager):
        """Test querying all relationship types."""
        # Add different types
        graph_manager.add_relationship('alice', 'bob', 'follows')
        graph_manager.add_relationship('alice', 'charlie', 'likes')
        
        # Query all types
        all_rels = graph_manager.get_outgoing('alice', None)
        assert len(all_rels) == 2
    
    def test_remove_relationship(self, graph_manager):
        """Test removing relationships."""
        # Add relationship
        graph_manager.add_relationship('alice', 'bob', 'follows')
        assert graph_manager.has_relationship('alice', 'bob')
        
        # Remove it
        removed = graph_manager.remove_relationship('alice', 'bob', 'follows')
        assert removed
        
        # Verify removal
        assert not graph_manager.has_relationship('alice', 'bob')
    
    def test_degree_calculation(self, graph_manager):
        """Test degree calculation in different directions."""
        # Create graph
        graph_manager.add_relationship('alice', 'bob', 'follows')
        graph_manager.add_relationship('alice', 'charlie', 'follows')
        graph_manager.add_relationship('dave', 'alice', 'follows')
        
        # Test degrees
        assert graph_manager.get_degree('alice', 'out') == 2
        assert graph_manager.get_degree('alice', 'in') == 1
        assert graph_manager.get_degree('alice', 'both') == 3
        assert graph_manager.get_degree('bob', 'both') == 1


@pytest.mark.xwnode_unit
class TestGraphManagerIsolation:
    """Test multi-tenant isolation features."""
    
    def test_isolation_key_set(self):
        """Test isolation key is set correctly."""
        gm = XWGraphManager(isolation_key="tenant_123")
        assert gm.isolation_key == "tenant_123"
    
    def test_valid_isolation_key(self):
        """Test valid isolation keys are accepted."""
        # Alphanumeric keys should work
        gm1 = XWGraphManager(isolation_key="tenant_123")
        gm2 = XWGraphManager(isolation_key="user_abc")
        gm3 = XWGraphManager(isolation_key="context_xyz_789")
        
        assert gm1.isolation_key == "tenant_123"
        assert gm2.isolation_key == "user_abc"
        assert gm3.isolation_key == "context_xyz_789"
    
    def test_operations_within_isolation_boundary(self):
        """Test operations within isolation boundary work correctly."""
        gm = XWGraphManager(isolation_key="tenant_a")
        
        # These should work (same isolation prefix)
        gm.add_relationship('tenant_a_user1', 'tenant_a_user2', 'follows')
        
        outgoing = gm.get_outgoing('tenant_a_user1', 'follows')
        assert len(outgoing) == 1
    
    def test_separate_instances_are_isolated(self):
        """Test that separate instances don't share data."""
        gm_a = XWGraphManager(isolation_key="tenant_a")
        gm_b = XWGraphManager(isolation_key="tenant_b")
        
        # Add to tenant A
        gm_a.add_relationship('user1', 'user2', 'follows')
        
        # Add to tenant B
        gm_b.add_relationship('user3', 'user4', 'follows')
        
        # Verify isolation
        assert len(gm_a.get_outgoing('user1')) == 1
        assert len(gm_b.get_outgoing('user3')) == 1
        assert len(gm_a.get_outgoing('user3')) == 0
        assert len(gm_b.get_outgoing('user1')) == 0


@pytest.mark.xwnode_unit
class TestGraphManagerCaching:
    """Test caching functionality."""
    
    def test_cache_hit_on_repeated_query(self, graph_manager):
        """Test cache hits on repeated queries."""
        # Add relationship
        graph_manager.add_relationship('alice', 'bob', 'follows')
        
        # First query - cache miss
        stats_before = graph_manager.get_stats()
        result1 = graph_manager.get_outgoing('alice', 'follows')
        
        # Second query - cache hit
        result2 = graph_manager.get_outgoing('alice', 'follows')
        stats_after = graph_manager.get_stats()
        
        # Results should be same
        assert result1 == result2
        
        # Cache should have hits
        assert stats_after['cache_hits'] > stats_before.get('cache_hits', 0)
    
    def test_cache_invalidation_on_add(self, graph_manager):
        """Test cache invalidation when adding relationships."""
        # Add and query
        graph_manager.add_relationship('alice', 'bob', 'follows')
        result1 = graph_manager.get_outgoing('alice', 'follows')
        
        # Add another relationship for same entity
        graph_manager.add_relationship('alice', 'charlie', 'follows')
        
        # Query again - should not get stale cached result
        result2 = graph_manager.get_outgoing('alice', 'follows')
        
        # Should have new data
        assert len(result2) == 2
        assert len(result1) == 1
    
    def test_cache_invalidation_on_remove(self, graph_manager):
        """Test cache invalidation when removing relationships."""
        # Add relationships
        graph_manager.add_relationship('alice', 'bob', 'follows')
        graph_manager.add_relationship('alice', 'charlie', 'follows')
        
        # Query and cache
        result1 = graph_manager.get_outgoing('alice', 'follows')
        assert len(result1) == 2
        
        # Remove one
        graph_manager.remove_relationship('alice', 'bob', 'follows')
        
        # Query again - should not get stale result
        result2 = graph_manager.get_outgoing('alice', 'follows')
        assert len(result2) == 1
    
    def test_clear_cache(self, graph_manager):
        """Test manual cache clearing."""
        # Add and query to populate cache
        graph_manager.add_relationship('alice', 'bob', 'follows')
        graph_manager.get_outgoing('alice', 'follows')
        
        # Clear cache
        graph_manager.clear_cache()
        
        # Stats should show cache cleared
        stats = graph_manager.get_stats()
        assert stats['cache_size'] == 0


@pytest.mark.xwnode_unit
class TestGraphManagerIndexing:
    """Test indexing functionality."""
    
    def test_outgoing_index(self, graph_manager):
        """Test outgoing relationship index."""
        # Add relationships
        graph_manager.add_relationship('alice', 'bob', 'follows')
        graph_manager.add_relationship('alice', 'charlie', 'follows')
        
        # Query should use index
        outgoing = graph_manager.get_outgoing('alice', 'follows')
        assert len(outgoing) == 2
        
        targets = [r['target'] for r in outgoing]
        assert 'bob' in targets
        assert 'charlie' in targets
    
    def test_incoming_index(self, graph_manager):
        """Test incoming relationship index."""
        # Add relationships
        graph_manager.add_relationship('alice', 'charlie', 'follows')
        graph_manager.add_relationship('bob', 'charlie', 'follows')
        
        # Query incoming
        incoming = graph_manager.get_incoming('charlie', 'follows')
        assert len(incoming) == 2
        
        sources = [r['source'] for r in incoming]
        assert 'alice' in sources
        assert 'bob' in sources
    
    def test_index_stats(self, graph_manager):
        """Test index statistics."""
        # Add relationships
        graph_manager.add_relationship('alice', 'bob', 'follows')
        graph_manager.add_relationship('bob', 'charlie', 'follows')
        
        stats = graph_manager.get_stats()
        
        assert stats['total_relationships'] == 2
        assert stats['indexed_sources'] >= 2
        assert stats['indexed_targets'] >= 2
    
    def test_clear_indexes(self, graph_manager):
        """Test clearing indexes."""
        # Add relationships
        graph_manager.add_relationship('alice', 'bob', 'follows')
        
        # Clear indexes
        graph_manager.clear_indexes()
        
        # Should be empty
        stats = graph_manager.get_stats()
        assert stats['total_relationships'] == 0


@pytest.mark.xwnode_unit
class TestGraphManagerEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_graph_queries(self, graph_manager):
        """Test querying empty graph."""
        outgoing = graph_manager.get_outgoing('nonexistent', 'follows')
        incoming = graph_manager.get_incoming('nonexistent', 'follows')
        
        assert outgoing == []
        assert incoming == []
    
    def test_nonexistent_entity(self, graph_manager):
        """Test querying nonexistent entity."""
        graph_manager.add_relationship('alice', 'bob', 'follows')
        
        # Query entity that doesn't exist
        result = graph_manager.get_outgoing('charlie', 'follows')
        assert result == []
    
    def test_nonexistent_relationship_type(self, graph_manager):
        """Test querying nonexistent relationship type."""
        graph_manager.add_relationship('alice', 'bob', 'follows')
        
        # Query different type
        result = graph_manager.get_outgoing('alice', 'likes')
        assert result == []
    
    def test_has_relationship_nonexistent(self, graph_manager):
        """Test has_relationship returns False for nonexistent."""
        assert not graph_manager.has_relationship('alice', 'bob')
    
    def test_remove_nonexistent_relationship(self, graph_manager):
        """Test removing nonexistent relationship."""
        removed = graph_manager.remove_relationship('alice', 'bob', 'follows')
        assert not removed
    
    def test_limit_parameter(self, graph_manager):
        """Test limit parameter works correctly."""
        # Add many relationships
        for i in range(10):
            graph_manager.add_relationship('alice', f'entity_{i}', 'follows')
        
        # Query with limit
        limited = graph_manager.get_outgoing('alice', 'follows', limit=5)
        assert len(limited) == 5
        
        # Query without limit
        all_rels = graph_manager.get_outgoing('alice', 'follows')
        assert len(all_rels) == 10

