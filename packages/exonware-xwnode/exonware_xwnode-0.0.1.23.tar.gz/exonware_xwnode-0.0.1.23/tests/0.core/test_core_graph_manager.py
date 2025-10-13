"""
#exonware/xwnode/tests/0.core/test_core_graph_manager.py

Core functionality tests for XWGraphManager (20% tests for 80% value).

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
import time
from exonware.xwnode.common.graph import XWGraphManager
from exonware.xwnode.defs import EdgeMode


@pytest.mark.xwnode_core
class TestGraphManagerCore:
    """Core graph manager tests - high value, fast execution."""
    
    def test_basic_relationship_operations(self):
        """Test add and query relationships - fundamental operations."""
        gm = XWGraphManager()
        
        # Add relationships
        rel_id = gm.add_relationship('alice', 'bob', 'follows')
        assert rel_id is not None
        assert 'rel_' in rel_id
        
        # Query outgoing
        outgoing = gm.get_outgoing('alice', 'follows')
        assert len(outgoing) == 1
        assert outgoing[0]['target'] == 'bob'
        assert outgoing[0]['type'] == 'follows'
        
        # Query incoming
        incoming = gm.get_incoming('bob', 'follows')
        assert len(incoming) == 1
        assert incoming[0]['source'] == 'alice'
    
    def test_multiple_relationship_types(self):
        """Test different relationship types are properly separated."""
        gm = XWGraphManager()
        
        # Add different types
        gm.add_relationship('alice', 'bob', 'follows')
        gm.add_relationship('alice', 'charlie', 'likes')
        gm.add_relationship('alice', 'dave', 'mentions')
        
        # Query by type
        follows = gm.get_outgoing('alice', 'follows')
        likes = gm.get_outgoing('alice', 'likes')
        mentions = gm.get_outgoing('alice', 'mentions')
        
        assert len(follows) == 1
        assert len(likes) == 1
        assert len(mentions) == 1
        
        # Query all types
        all_rels = gm.get_outgoing('alice', None)
        assert len(all_rels) == 3
    
    def test_o1_performance_characteristic(self):
        """Test O(1) lookup performance - critical for scalability."""
        gm = XWGraphManager(enable_indexing=True)
        
        # Add 10,000 relationships
        for i in range(10000):
            gm.add_relationship(f'entity_{i}', f'entity_{i+1}', 'connects')
        
        # Query should be O(1) - fast even with many relationships
        start = time.perf_counter()
        result = gm.get_outgoing('entity_5000', 'connects')
        elapsed = time.perf_counter() - start
        
        # Should complete in < 1ms (O(1) indexed lookup)
        assert elapsed < 0.001, f"Query took {elapsed*1000:.2f}ms, expected < 1ms"
        assert len(result) == 1
    
    def test_cache_functionality(self):
        """Test caching improves repeated query performance."""
        gm = XWGraphManager(enable_caching=True, enable_indexing=True)
        
        # Add relationships
        for i in range(100):
            gm.add_relationship('alice', f'entity_{i}', 'follows')
        
        # First query - cache miss
        stats_before = gm.get_stats()
        result1 = gm.get_outgoing('alice', 'follows')
        
        # Second query - should hit cache
        result2 = gm.get_outgoing('alice', 'follows')
        stats_after = gm.get_stats()
        
        # Verify results are same
        assert len(result1) == len(result2) == 100
        
        # Verify cache was used
        assert stats_after['cache_hits'] > stats_before['cache_hits']
    
    def test_bidirectional_queries(self):
        """Test both incoming and outgoing relationships."""
        gm = XWGraphManager()
        
        # Create a simple graph:
        # alice -> bob
        # alice -> charlie
        # dave -> alice
        gm.add_relationship('alice', 'bob', 'follows')
        gm.add_relationship('alice', 'charlie', 'follows')
        gm.add_relationship('dave', 'alice', 'follows')
        
        # Alice follows 2 people
        alice_following = gm.get_outgoing('alice', 'follows')
        assert len(alice_following) == 2
        
        # 1 person follows Alice
        alice_followers = gm.get_incoming('alice', 'follows')
        assert len(alice_followers) == 1
        assert alice_followers[0]['source'] == 'dave'
    
    def test_has_relationship(self):
        """Test relationship existence check."""
        gm = XWGraphManager()
        
        gm.add_relationship('alice', 'bob', 'follows')
        
        # Should find existing relationship
        assert gm.has_relationship('alice', 'bob', 'follows')
        assert gm.has_relationship('alice', 'bob')  # No type filter
        
        # Should not find non-existent relationships
        assert not gm.has_relationship('bob', 'alice', 'follows')
        assert not gm.has_relationship('alice', 'charlie')
    
    def test_remove_relationship(self):
        """Test removing relationships."""
        gm = XWGraphManager()
        
        # Add relationships
        gm.add_relationship('alice', 'bob', 'follows')
        gm.add_relationship('alice', 'charlie', 'follows')
        
        # Verify they exist
        assert len(gm.get_outgoing('alice', 'follows')) == 2
        
        # Remove one
        removed = gm.remove_relationship('alice', 'bob', 'follows')
        assert removed
        
        # Verify removal
        assert len(gm.get_outgoing('alice', 'follows')) == 1
        assert not gm.has_relationship('alice', 'bob')
    
    def test_empty_graph(self):
        """Test operations on empty graph."""
        gm = XWGraphManager()
        
        # Query empty graph
        outgoing = gm.get_outgoing('nonexistent', 'follows')
        incoming = gm.get_incoming('nonexistent', 'follows')
        
        assert outgoing == []
        assert incoming == []
        assert not gm.has_relationship('alice', 'bob')
    
    def test_get_degree(self):
        """Test degree calculation."""
        gm = XWGraphManager()
        
        # Create relationships
        gm.add_relationship('alice', 'bob', 'follows')
        gm.add_relationship('alice', 'charlie', 'follows')
        gm.add_relationship('dave', 'alice', 'follows')
        
        # Check degrees
        assert gm.get_degree('alice', direction='out') == 2
        assert gm.get_degree('alice', direction='in') == 1
        assert gm.get_degree('alice', direction='both') == 3
    
    def test_common_neighbors(self):
        """Test finding common neighbors."""
        gm = XWGraphManager()
        
        # alice and bob both follow charlie and dave
        gm.add_relationship('alice', 'charlie', 'follows')
        gm.add_relationship('alice', 'dave', 'follows')
        gm.add_relationship('bob', 'charlie', 'follows')
        gm.add_relationship('bob', 'dave', 'follows')
        gm.add_relationship('alice', 'eve', 'follows')  # Only alice
        
        # Find common neighbors
        common = gm.get_common_neighbors('alice', 'bob', 'follows')
        assert len(common) == 2
        assert 'charlie' in common
        assert 'dave' in common
        assert 'eve' not in common

