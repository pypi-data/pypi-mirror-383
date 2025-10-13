"""
#exonware/xwnode/tests/0.core/test_trie_strategy.py

Comprehensive tests for TRIE node strategy.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 12-Oct-2025
"""

import pytest
from exonware.xwnode.nodes.strategies.trie import TrieStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait


@pytest.mark.xwnode_core
class TestTrieCore:
    """Core functionality tests for TRIE strategy."""
    
    def test_initialization(self):
        """Test initialization."""
        strategy = TrieStrategy()
        assert strategy is not None
        assert len(strategy) == 0
        assert strategy.mode == NodeMode.TRIE
    
    def test_insert_and_search(self):
        """Test basic insert and search."""
        strategy = TrieStrategy()
        strategy.put("hello", "world")
        assert strategy.get("hello") == "world"
        assert strategy.has("hello")
    
    def test_prefix_search(self):
        """Test prefix-based searching (Trie's strength)."""
        strategy = TrieStrategy()
        words = ["hello", "help", "hell", "world"]
        for word in words:
            strategy.put(word, word.upper())
        
        # All words should be accessible
        for word in words:
            assert strategy.has(word)
    
    def test_delete_word(self):
        """Test deleting words."""
        strategy = TrieStrategy()
        strategy.put("hello", "HELLO")
        strategy.put("help", "HELP")
        
        assert strategy.delete("hello")
        assert not strategy.has("hello")
        assert strategy.has("help")  # Other words remain
    
    def test_empty_string(self):
        """Test handling of empty string."""
        strategy = TrieStrategy()
        strategy.put("", "empty")
        assert strategy.get("") == "empty"
    
    def test_iteration(self):
        """Test iteration over all keys."""
        strategy = TrieStrategy()
        words = ["cat", "car", "card", "care"]
        for word in words:
            strategy.put(word, word.upper())
        
        keys = list(strategy.keys())
        assert len(keys) == len(words)
    
    def test_clear(self):
        """Test clearing all data."""
        strategy = TrieStrategy()
        for word in ["hello", "world", "test"]:
            strategy.put(word, word)
        
        strategy.clear()
        assert len(strategy) == 0
    
    def test_to_native(self):
        """Test conversion to dict."""
        strategy = TrieStrategy()
        data = {"hello": 1, "world": 2}
        for k, v in data.items():
            strategy.put(k, v)
        
        native = strategy.to_native()
        assert isinstance(native, dict)


@pytest.mark.xwnode_performance
class TestTriePerformance:
    """Performance validation for Trie."""
    
    def test_time_complexity_ok(self):
        """Validate O(k) complexity where k=key length."""
        import time
        
        # Create tries with different numbers of words
        strategies = {}
        for num_words in [100, 1000, 10000]:
            s = TrieStrategy()
            for i in range(num_words):
                s.put(f"word_{i:06d}", i)
            strategies[num_words] = s
        
        # Search time should depend on KEY LENGTH, not number of words
        timings = {}
        for size, strategy in strategies.items():
            measurements = []
            for _ in range(100):
                start = time.perf_counter()
                strategy.get(f"word_{size//2:06d}")  # Same key length
                elapsed = time.perf_counter() - start
                measurements.append(elapsed)
            measurements.sort()
            timings[size] = measurements[len(measurements)//2]
        
        # Time should be relatively constant (depends on key length, not dataset size)
        ratio = timings[10000] / timings[100]
        assert ratio < 5.0, f"Expected O(k), got ratio {ratio:.2f}"
    
    def test_prefix_search_performance(self):
        """Test that prefix searches are efficient."""
        import time
        
        strategy = TrieStrategy()
        # Insert 1000 words
        for i in range(1000):
            strategy.put(f"prefix_{i:04d}", i)
        
        # Prefix search should be fast
        start = time.perf_counter()
        count = 0
        for key in strategy.keys():
            if key.startswith("prefix_05"):
                count += 1
        elapsed = time.perf_counter() - start
        
        assert elapsed < 0.01, f"Prefix iteration took {elapsed*1000:.2f}ms"


@pytest.mark.xwnode_core
class TestTrieEdgeCases:
    """Edge case tests for Trie."""
    
    def test_empty_operations(self):
        """Test operations on empty trie."""
        strategy = TrieStrategy()
        assert len(strategy) == 0
        assert strategy.get("any") is None
        assert not strategy.has("any")
    
    def test_single_character_keys(self):
        """Test single character keys."""
        strategy = TrieStrategy()
        strategy.put("a", 1)
        strategy.put("b", 2)
        assert strategy.get("a") == 1
        assert strategy.get("b") == 2
    
    def test_unicode_keys(self, multilingual_data):
        """Test Unicode support."""
        strategy = TrieStrategy()
        for k, v in multilingual_data.items():
            strategy.put(k, v)
        
        assert strategy.get("chinese") == "你好世界"
    
    def test_overlapping_prefixes(self):
        """Test words with overlapping prefixes."""
        strategy = TrieStrategy()
        words = ["test", "testing", "tested", "tester", "tests"]
        for word in words:
            strategy.put(word, len(word))
        
        # All should be accessible despite overlap
        for word in words:
            assert strategy.has(word)
            assert strategy.get(word) == len(word)
