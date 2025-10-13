"""
#exonware/xwnode/tests/0.core/test_veb_tree_strategy.py

Core tests for van Emde Boas Tree strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.defs import NodeMode
from exonware.xwnode.nodes.strategies.veb_tree import VebTreeStrategy
from exonware.xwnode.errors import XWNodeValueError


@pytest.mark.xwnode_core
class TestVebTreeStrategyCore:
    """Core tests for vEB tree strategy - Priority: Security, Usability."""
    
    def test_create_veb_tree(self):
        """
        Test basic vEB tree creation.
        
        WHY this test:
        - Validates construction with power-of-2 universe
        - Tests basic put/get operations
        - Priority: Usability - simple API works
        """
        tree = VebTreeStrategy(universe_size=16)
        
        assert tree is not None
        assert tree.mode == NodeMode.VEB_TREE
        assert tree.universe_size == 16
        assert len(tree) == 0
    
    def test_insert_and_retrieve(self):
        """
        Test insert and retrieve operations.
        
        WHY this test:
        - Validates O(log log U) operations
        - Tests correctness of vEB structure
        - Priority: Performance - fast operations
        """
        tree = VebTreeStrategy(universe_size=256)
        
        # Insert keys
        tree.put(5, "five")
        tree.put(10, "ten")
        tree.put(50, "fifty")
        
        # Retrieve
        assert tree.get(5) == "five"
        assert tree.get(10) == "ten"
        assert tree.get(50) == "fifty"
        assert tree.get(99) is None
        
        assert len(tree) == 3
    
    def test_universe_boundary_validation(self):
        """
        Test universe size validation.
        
        WHY this test:
        - Priority #1: Security - validates bounds
        - Prevents buffer overflows
        - Ensures power-of-2 requirement
        """
        # Must be power of 2
        with pytest.raises(XWNodeValueError, match="power of 2"):
            VebTreeStrategy(universe_size=100)
        
        # Must be positive
        with pytest.raises(XWNodeValueError, match="power of 2"):
            VebTreeStrategy(universe_size=0)
        
        # Valid powers of 2
        tree = VebTreeStrategy(universe_size=64)
        assert tree.universe_size == 64
    
    def test_key_bounds_validation(self):
        """
        Test key bounds validation.
        
        WHY this test:
        - Priority #1: Security - prevents out-of-bounds access
        - Validates input sanitization
        - Prevents malicious inputs
        """
        tree = VebTreeStrategy(universe_size=16)
        
        # Out of bounds
        with pytest.raises(XWNodeValueError, match="out of.*bounds"):
            tree.put(-1, "negative")
        
        with pytest.raises(XWNodeValueError, match="out of.*bounds"):
            tree.put(16, "too large")
        
        # Valid bounds
        tree.put(0, "zero")
        tree.put(15, "fifteen")
        assert tree.get(0) == "zero"
        assert tree.get(15) == "fifteen"
    
    def test_integer_key_requirement(self):
        """
        Test that non-integer keys are rejected.
        
        WHY this test:
        - Priority #1: Security - type safety
        - Validates API contract
        - Clear error messages
        """
        tree = VebTreeStrategy(universe_size=32)
        
        with pytest.raises(XWNodeValueError, match="integer keys"):
            tree.put("string_key", "value")
        
        with pytest.raises(XWNodeValueError, match="integer keys"):
            tree.put(3.14, "pi")
    
    def test_min_max_operations(self):
        """
        Test O(1) min/max queries.
        
        WHY this test:
        - Priority #4: Performance - validates O(1) extreme queries
        - Tests key vEB feature
        - Validates caching mechanism
        """
        tree = VebTreeStrategy(universe_size=64)
        
        # Empty tree
        assert tree.get_min() is None
        assert tree.get_max() is None
        
        # Add elements
        tree.put(10, "ten")
        tree.put(30, "thirty")
        tree.put(5, "five")
        tree.put(50, "fifty")
        
        # Min/max should be O(1)
        assert tree.get_min() == 5
        assert tree.get_max() == 50
    
    def test_successor_predecessor(self):
        """
        Test successor and predecessor operations.
        
        WHY this test:
        - Validates ordered operations
        - Tests O(log log U) complexity
        - Priority: Performance
        """
        tree = VebTreeStrategy(universe_size=128)
        
        tree.put(10, "ten")
        tree.put(20, "twenty")
        tree.put(40, "forty")
        tree.put(80, "eighty")
        
        # Successor tests
        assert tree.successor(10) == 20
        assert tree.successor(15) == 20
        assert tree.successor(40) == 80
        assert tree.successor(80) is None
        
        # Predecessor tests
        assert tree.predecessor(80) == 40
        assert tree.predecessor(50) == 40
        assert tree.predecessor(20) == 10
        assert tree.predecessor(10) is None
    
    def test_delete_operation(self):
        """
        Test deletion maintains vEB structure.
        
        WHY this test:
        - Validates deletion correctness
        - Tests structure integrity
        - Priority: Maintainability
        """
        tree = VebTreeStrategy(universe_size=32)
        
        tree.put(5, "five")
        tree.put(10, "ten")
        tree.put(15, "fifteen")
        
        assert len(tree) == 3
        
        # Delete middle element
        assert tree.delete(10) == True
        assert len(tree) == 2
        assert tree.has(10) == False
        assert tree.has(5) == True
        assert tree.has(15) == True
        
        # Delete non-existent
        assert tree.delete(99) == False
    
    def test_range_query(self):
        """
        Test range query operations.
        
        WHY this test:
        - Validates ordered operations
        - Tests practical use case
        - Priority: Usability
        """
        tree = VebTreeStrategy(universe_size=128)
        
        for i in [5, 10, 15, 20, 25, 30, 35]:
            tree.put(i, f"value_{i}")
        
        # Range query
        results = tree.range_query(10, 30)
        keys = [k for k, v in results]
        
        assert 10 in keys
        assert 15 in keys
        assert 20 in keys
        assert 25 in keys
        assert 30 in keys
        assert 5 not in keys
        assert 35 not in keys
    
    def test_iteration_order(self):
        """
        Test iteration returns sorted keys.
        
        WHY this test:
        - Validates ordered trait
        - Tests iterator correctness
        - Priority: Usability
        """
        tree = VebTreeStrategy(universe_size=64)
        
        # Insert in random order
        for key in [30, 10, 50, 5, 25, 15]:
            tree.put(key, f"val_{key}")
        
        # Should iterate in sorted order
        keys = list(tree.keys())
        assert keys == [5, 10, 15, 25, 30, 50]
    
    def test_large_universe_performance(self):
        """
        Test performance with larger universe.
        
        WHY this test:
        - Validates O(log log U) advantage
        - Tests practical scenario (32-bit universe)
        - Priority: Performance
        """
        # 16-bit universe
        tree = VebTreeStrategy(universe_size=65536)
        
        # Insert sparse keys
        keys = [100, 1000, 10000, 30000, 60000]
        for key in keys:
            tree.put(key, f"value_{key}")
        
        # All should be accessible
        for key in keys:
            assert tree.has(key)
            assert tree.get(key) == f"value_{key}"
    
    def test_memory_usage_stats(self):
        """
        Test memory usage statistics.
        
        WHY this test:
        - Validates monitoring capability
        - Tests lazy allocation
        - Priority: Performance
        """
        tree = VebTreeStrategy(universe_size=256)
        
        for i in range(0, 20, 2):
            tree.put(i, f"val_{i}")
        
        stats = tree.get_memory_usage()
        
        assert 'allocated_nodes' in stats
        assert 'universe_size' in stats
        assert 'stored_values' in stats
        assert stats['stored_values'] == 10
        assert stats['universe_size'] == 256
    
    def test_create_from_data(self):
        """
        Test factory method.
        
        WHY this test:
        - Validates factory pattern
        - Tests convenience creation
        - Priority: Usability
        """
        data = {0: "zero", 5: "five", 10: "ten"}
        tree = VebTreeStrategy.create_from_data(data, universe_size=32)
        
        assert len(tree) == 3
        assert tree.get(0) == "zero"
        assert tree.get(5) == "five"
        assert tree.get(10) == "ten"
    
    def test_clear_operation(self):
        """
        Test clear removes all data.
        
        WHY this test:
        - Validates cleanup
        - Tests structure reset
        - Priority: Maintainability
        """
        tree = VebTreeStrategy(universe_size=64)
        
        tree.put(5, "five")
        tree.put(10, "ten")
        assert len(tree) == 2
        
        tree.clear()
        assert len(tree) == 0
        assert tree.is_empty()
        assert tree.get_min() is None
        assert tree.get_max() is None
    
    def test_edge_cases(self):
        """
        Test edge cases for robustness.
        
        WHY this test:
        - Priority #1: Security - handles edge cases
        - Tests boundary conditions
        - Ensures no crashes
        """
        tree = VebTreeStrategy(universe_size=4)
        
        # Minimum universe (2^2 = 4)
        tree.put(0, "zero")
        tree.put(3, "three")
        
        assert tree.get_min() == 0
        assert tree.get_max() == 3
        
        # Duplicate inserts
        tree.put(0, "zero_updated")
        assert tree.get(0) == "zero_updated"
        assert len(tree) == 2  # Count shouldn't increase


@pytest.mark.xwnode_core
@pytest.mark.xwnode_performance
class TestVebTreePerformance:
    """Performance-specific tests for vEB tree."""
    
    def test_log_log_complexity(self):
        """
        Verify O(log log U) complexity advantage.
        
        WHY this test:
        - Priority #4: Performance
        - Validates core vEB benefit
        - Compares with theoretical complexity
        """
        import math
        
        tree = VebTreeStrategy(universe_size=65536)  # 2^16
        
        # Theoretical depth should be low
        depth = tree.get_depth()
        expected_depth = math.ceil(math.log2(math.log2(65536)))
        
        assert depth <= expected_depth + 1  # Allow small overhead
        assert depth < 10  # Much less than log(65536) ≈ 16
    
    def test_sparse_data_efficiency(self):
        """
        Test lazy allocation for sparse data.
        
        WHY this test:
        - Validates memory efficiency
        - Tests lazy cluster creation
        - Priority: Performance
        """
        tree = VebTreeStrategy(universe_size=65536)
        
        # Insert only 10 elements in large universe
        for i in range(10):
            tree.put(i * 1000, f"val_{i}")
        
        stats = tree.get_memory_usage()
        
        # Should not allocate entire universe
        assert stats['allocated_nodes'] < tree.universe_size
        assert stats['memory_efficiency'] > 0  # Some efficiency


@pytest.mark.xwnode_core
class TestVebTreeTraits:
    """Test trait support for vEB tree."""
    
    def test_supported_traits(self):
        """
        Test that vEB tree supports correct traits.
        
        WHY this test:
        - Validates trait system integration
        - Tests capability declaration
        - Priority: Extensibility
        """
        from exonware.xwnode.defs import NodeTrait
        
        tree = VebTreeStrategy()
        traits = tree.get_supported_traits()
        
        assert NodeTrait.ORDERED in traits
        assert NodeTrait.INDEXED in traits
        assert NodeTrait.FAST_INSERT in traits
    
    def test_strategy_type(self):
        """
        Test STRATEGY_TYPE classification.
        
        WHY this test:
        - Validates type system integration
        - Tests proper classification
        - Priority: Maintainability
        """
        from exonware.xwnode.nodes.strategies.contracts import NodeType
        
        assert VebTreeStrategy.STRATEGY_TYPE == NodeType.TREE

