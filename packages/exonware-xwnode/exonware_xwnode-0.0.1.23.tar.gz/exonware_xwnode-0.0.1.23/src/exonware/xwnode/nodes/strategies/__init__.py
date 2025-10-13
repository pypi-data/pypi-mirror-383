"""
Node Strategies Package

This package contains all node strategy implementations organized by type:
- Linear strategies (arrays, lists, stacks, queues)
- Tree strategies (tries, heaps, BSTs)
- Graph strategies (union-find, neural graphs)

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.23
Generation Date: January 2, 2025
"""

from .base import ANodeStrategy, ANodeLinearStrategy, ANodeTreeStrategy, ANodeGraphStrategy

# Linear strategies
from .array_list import ArrayListStrategy
from .linked_list import LinkedListStrategy

# Tree strategies
from .trie import TrieStrategy
from .heap import HeapStrategy
from .aho_corasick import AhoCorasickStrategy

# Graph strategies
from .hash_map import HashMapStrategy
from .union_find import UnionFindStrategy

# Advanced specialized strategies
from .veb_tree import VebTreeStrategy
from .dawg import DawgStrategy
from .hopscotch_hash import HopscotchHashStrategy
from .interval_tree import IntervalTreeStrategy
from .kd_tree import KdTreeStrategy
from .rope import RopeStrategy
from .crdt_map import CRDTMapStrategy
from .bloomier_filter import BloomierFilterStrategy

__all__ = [
    # Base classes
    'ANodeStrategy',
    'ANodeLinearStrategy', 
    'ANodeTreeStrategy',
    'ANodeGraphStrategy',
    
    # Linear strategies
    'ArrayListStrategy',
    'LinkedListStrategy',
    
    # Tree strategies
    'TrieStrategy',
    'HeapStrategy',
    'AhoCorasickStrategy',
    
    # Graph strategies
    'HashMapStrategy',
    'UnionFindStrategy',
    
    # Advanced specialized strategies
    'VebTreeStrategy',
    'DawgStrategy',
    'HopscotchHashStrategy',
    'IntervalTreeStrategy',
    'KdTreeStrategy',
    'RopeStrategy',
    'CRDTMapStrategy',
    'BloomierFilterStrategy',
]
