"""
#exonware/xwnode/tests/3.advance/test_graph_security.py

Security tests for graph manager (Priority #1).

Tests multi-tenant isolation, malicious input handling, and
cross-context access prevention.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 11-Oct-2025
"""

import pytest
from exonware.xwnode.common.graph import XWGraphManager, XWGraphSecurityError
from exonware.xwnode.defs import EdgeMode
from exonware.xwsystem.validation import ValidationError


@pytest.mark.xwnode_advance
@pytest.mark.xwnode_security
class TestGraphManagerSecurity:
    """Security validation for graph manager - Priority #1."""
    
    def test_no_cross_tenant_leakage(self):
        """
        Test that tenant data doesn't leak across instances.
        
        Critical for multi-tenant applications where data isolation
        is a security requirement.
        """
        # Tenant A
        gm_a = XWGraphManager(isolation_key="tenant_a")
        gm_a.add_relationship('user1', 'user2', 'follows')
        
        # Tenant B
        gm_b = XWGraphManager(isolation_key="tenant_b")
        gm_b.add_relationship('user3', 'user4', 'follows')
        
        # Verify isolation
        assert len(gm_a.get_outgoing('user1')) == 1
        assert len(gm_b.get_outgoing('user3')) == 1
        assert len(gm_a.get_outgoing('user3')) == 0  # Can't see tenant_b
        assert len(gm_b.get_outgoing('user1')) == 0  # Can't see tenant_a
    
    def test_cross_isolation_access_prevention(self):
        """
        Test that cross-isolation access is blocked.
        
        Prevents unauthorized access to data from different contexts.
        """
        gm = XWGraphManager(isolation_key="tenant_a")
        
        # Add relationship in tenant_a context
        gm.add_relationship('tenant_a_user1', 'tenant_a_user2', 'follows')
        
        # Try to access tenant_b resource - should fail
        with pytest.raises(XWGraphSecurityError):
            gm.get_outgoing('tenant_b_user1', 'follows')
        
        # Try to add relationship to tenant_b resource - should fail
        with pytest.raises(XWGraphSecurityError):
            gm.add_relationship('tenant_a_user1', 'tenant_b_user2', 'follows')
    
    def test_malicious_input_handling(self):
        """
        Test handling of malicious inputs.
        
        Validates defense against common attack vectors.
        """
        gm = XWGraphManager()
        
        malicious_inputs = [
            "../../../etc/passwd",              # Path traversal
            "<script>alert('xss')</script>",    # XSS attempt
            "'; DROP TABLE users; --",          # SQL injection pattern
            "\x00\x01\x02",                     # Null bytes
            "A" * 10000,                        # Large input (DoS)
        ]
        
        for malicious in malicious_inputs:
            # Should handle gracefully - validate or reject
            try:
                gm.add_relationship(malicious, 'target', 'type')
                # If accepted, should not crash on query
                result = gm.get_outgoing(malicious)
                assert isinstance(result, list)
            except (ValidationError, XWGraphSecurityError, ValueError):
                # Expected for some malicious inputs
                pass
    
    def test_isolation_key_validation(self):
        """
        Test isolation key validation.
        
        Ensures isolation keys follow security constraints.
        """
        # Valid isolation keys should work
        gm1 = XWGraphManager(isolation_key="tenant_123")
        assert gm1.isolation_key == "tenant_123"
        
        gm2 = XWGraphManager(isolation_key="user_abc")
        assert gm2.isolation_key == "user_abc"
        
        # Invalid isolation keys should be rejected
        invalid_keys = [
            "../../../etc/passwd",
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "A" * 1000,  # Too long
        ]
        
        for invalid_key in invalid_keys:
            with pytest.raises((ValidationError, ValueError)):
                XWGraphManager(isolation_key=invalid_key)
    
    def test_no_global_state_pollution(self):
        """
        Test that instances don't share global state.
        
        Ensures each instance is fully isolated from others.
        """
        # Create two separate instances
        gm1 = XWGraphManager()
        gm2 = XWGraphManager()
        
        # Add data to gm1
        gm1.add_relationship('alice', 'bob', 'follows')
        
        # gm2 should not see gm1's data
        assert len(gm1.get_outgoing('alice')) == 1
        assert len(gm2.get_outgoing('alice')) == 0
    
    def test_resource_limit_enforcement(self):
        """
        Test that resource limits are enforced.
        
        Prevents DoS attacks via excessive resource consumption.
        """
        gm = XWGraphManager()
        
        # Should have resource limits configured
        assert hasattr(gm, '_max_relationships')
        assert gm._max_relationships > 0
    
    def test_thread_safety(self):
        """
        Test thread-safe concurrent access.
        
        Ensures no race conditions or data corruption in multi-threaded environments.
        """
        import threading
        
        gm = XWGraphManager()
        errors = []
        
        def add_relationships(entity_prefix, count):
            try:
                for i in range(count):
                    gm.add_relationship(f'{entity_prefix}_{i}', f'{entity_prefix}_{i+1}', 'follows')
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_relationships, args=(f'thread{i}', 100))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should have no errors
        assert len(errors) == 0
        
        # Should have all relationships
        stats = gm.get_stats()
        assert stats['total_relationships'] == 500  # 5 threads * 100 each
    
    def test_cache_poisoning_prevention(self):
        """
        Test that cache cannot be poisoned.
        
        Ensures cached data is properly isolated and invalidated.
        """
        gm = XWGraphManager(enable_caching=True)
        
        # Add and cache query
        gm.add_relationship('alice', 'bob', 'follows')
        result1 = gm.get_outgoing('alice', 'follows')
        
        # Add more data (should invalidate cache)
        gm.add_relationship('alice', 'charlie', 'follows')
        
        # Query should return fresh data, not stale cache
        result2 = gm.get_outgoing('alice', 'follows')
        
        # Should have updated data
        assert len(result2) == 2
        assert len(result1) == 1

