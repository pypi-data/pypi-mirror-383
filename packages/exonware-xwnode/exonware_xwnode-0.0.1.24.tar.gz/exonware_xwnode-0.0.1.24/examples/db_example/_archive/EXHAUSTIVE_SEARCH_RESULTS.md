# Exhaustive Strategy Search Results

## Test Configuration

- **Total Combinations Tested:** 760
- **Successful Tests:** 760
- **Quick Mode:** Disabled
- **Dataset:** 100 users, 60 posts, 40 comments, 200 relationships
- **Operations:** Insert, Read, Update, Relationship queries

## Predictions

### 1X Scale
- **Predicted Winner:** HASH_MAP + None
- **Reasoning:** O(1) lookups dominate small datasets, zero graph overhead
- **Estimated Time:** 11.5ms

### 10X Scale
- **Predicted Winner:** B_TREE + ADJ_LIST
- **Reasoning:** B_TREE cache hits increase, ADJ_LIST is sparse-efficient
- **Estimated Time:** 350.0ms

### Dark Horse
- **Predicted Winner:** LSM_TREE + None
- **Reasoning:** Write-optimized inserts + zero edge overhead
- **Estimated Time:** 360.0ms

## Top 20 Fastest Configurations

| Rank | Configuration | Node Mode | Edge Mode | Total Time | Memory | Insert | Read | Update | Relations |
|------|---------------|-----------|-----------|------------|--------|--------|------|--------|----------|
| 1 [1st] | CUCKOO_HASH+CSR | CUCKOO_HASH | CSR | 1.60ms | 206.1MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 2 [2nd] | CUCKOO_HASH+ADJ_MATRIX | CUCKOO_HASH | ADJ_MATRIX | 1.61ms | 206.1MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 3 [3rd] | B_TREE+TEMPORAL_EDGESET | B_TREE | TEMPORAL_EDGESET | 1.61ms | 206.4MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 4  | STACK+BLOCK_ADJ_MATRIX | STACK | BLOCK_ADJ_MATRIX | 1.62ms | 210.5MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 5  | STACK+R_TREE | STACK | R_TREE | 1.62ms | 210.5MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 6  | STACK+HYPEREDGE_SET | STACK | HYPEREDGE_SET | 1.62ms | 210.5MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 7  | COUNT_MIN_SKETCH+ADJ_LIST | COUNT_MIN_SKETCH | ADJ_LIST | 1.63ms | 206.8MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 8  | CUCKOO_HASH+DYNAMIC_ADJ_LIST | CUCKOO_HASH | DYNAMIC_ADJ_LIST | 1.63ms | 206.1MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 9  | STACK+ADJ_MATRIX | STACK | ADJ_MATRIX | 1.63ms | 210.5MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 10  | QUEUE+TEMPORAL_EDGESET | QUEUE | TEMPORAL_EDGESET | 1.64ms | 210.6MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 11  | QUEUE+R_TREE | QUEUE | R_TREE | 1.64ms | 210.6MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 12  | ARRAY_LIST+HYPEREDGE_SET | ARRAY_LIST | HYPEREDGE_SET | 1.64ms | 210.3MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 13  | PRIORITY_QUEUE+CSC | PRIORITY_QUEUE | CSC | 1.64ms | 210.6MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 14  | DEQUE+EDGE_PROPERTY_STORE | DEQUE | EDGE_PROPERTY_STORE | 1.64ms | 210.7MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 15  | B_TREE+ADJ_MATRIX | B_TREE | ADJ_MATRIX | 1.64ms | 206.4MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 16  | STACK+BIDIR_WRAPPER | STACK | BIDIR_WRAPPER | 1.64ms | 210.5MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 17  | ARRAY_LIST+R_TREE | ARRAY_LIST | R_TREE | 1.64ms | 210.3MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 18  | STACK+ADJ_LIST | STACK | ADJ_LIST | 1.64ms | 210.4MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 19  | HASH_MAP+OCTREE | HASH_MAP | OCTREE | 1.64ms | 210.0MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |
| 20  | DEQUE+R_TREE | DEQUE | R_TREE | 1.65ms | 210.7MB | 1.5ms | 0.0ms | 0.0ms | 0.1ms |

## Top 20 Most Memory Efficient

| Rank | Configuration | Node Mode | Edge Mode | Memory | Total Time |
|------|---------------|-----------|-----------|--------|------------|
| 1 | HEAP+OCTREE | HEAP | OCTREE | 205.8MB | 1.81ms |
| 2 | HEAP+FLOW_NETWORK | HEAP | FLOW_NETWORK | 205.8MB | 1.65ms |
| 3 | HEAP+WEIGHTED_GRAPH | HEAP | WEIGHTED_GRAPH | 205.8MB | 1.76ms |
| 4 | HEAP+NEURAL_GRAPH | HEAP | NEURAL_GRAPH | 205.8MB | 1.76ms |
| 5 | SET_HASH+None | SET_HASH | None | 205.9MB | 1.88ms |
| 6 | SET_HASH+ADJ_LIST | SET_HASH | ADJ_LIST | 205.9MB | 1.84ms |
| 7 | SET_HASH+TREE_GRAPH_BASIC | SET_HASH | TREE_GRAPH_BASIC | 205.9MB | 1.91ms |
| 8 | SET_HASH+ADJ_MATRIX | SET_HASH | ADJ_MATRIX | 205.9MB | 1.79ms |
| 9 | SET_HASH+DYNAMIC_ADJ_LIST | SET_HASH | DYNAMIC_ADJ_LIST | 205.9MB | 1.79ms |
| 10 | SET_HASH+BLOCK_ADJ_MATRIX | SET_HASH | BLOCK_ADJ_MATRIX | 205.9MB | 1.81ms |
| 11 | SET_HASH+CSC | SET_HASH | CSC | 205.9MB | 1.80ms |
| 12 | SET_HASH+CSR | SET_HASH | CSR | 205.9MB | 1.80ms |
| 13 | SET_HASH+COO | SET_HASH | COO | 205.9MB | 1.78ms |
| 14 | SET_HASH+BIDIR_WRAPPER | SET_HASH | BIDIR_WRAPPER | 205.9MB | 1.78ms |
| 15 | SET_HASH+TEMPORAL_EDGESET | SET_HASH | TEMPORAL_EDGESET | 205.9MB | 1.77ms |
| 16 | SET_HASH+EDGE_PROPERTY_STORE | SET_HASH | EDGE_PROPERTY_STORE | 205.9MB | 1.79ms |
| 17 | SET_HASH+HYPEREDGE_SET | SET_HASH | HYPEREDGE_SET | 205.9MB | 1.79ms |
| 18 | SET_HASH+R_TREE | SET_HASH | R_TREE | 205.9MB | 1.76ms |
| 19 | SET_HASH+QUADTREE | SET_HASH | QUADTREE | 205.9MB | 1.77ms |
| 20 | SET_HASH+FLOW_NETWORK | SET_HASH | FLOW_NETWORK | 205.9MB | 1.75ms |

## Prediction Accuracy

**Predicted Winner:** HASH_MAP + None
**Actual Winner:** CUCKOO_HASH+CSR
**Prediction Status:** INCORRECT

**Why the difference:**
- Predicted: O(1) lookups dominate small datasets, zero graph overhead
- Actual winner may have optimizations we didn't account for

## Strategy Analysis

### Best Edge Mode for Each Node Mode

| Node Mode | Best Edge Mode | Time | Memory |
|-----------|----------------|------|--------|
| CUCKOO_HASH | CSR | 1.60ms | 206.1MB |
| B_TREE | TEMPORAL_EDGESET | 1.61ms | 206.4MB |
| STACK | BLOCK_ADJ_MATRIX | 1.62ms | 210.5MB |
| COUNT_MIN_SKETCH | ADJ_LIST | 1.63ms | 206.8MB |
| QUEUE | TEMPORAL_EDGESET | 1.64ms | 210.6MB |
| ARRAY_LIST | HYPEREDGE_SET | 1.64ms | 210.3MB |
| PRIORITY_QUEUE | CSC | 1.64ms | 210.6MB |
| DEQUE | EDGE_PROPERTY_STORE | 1.64ms | 210.7MB |
| HASH_MAP | OCTREE | 1.64ms | 210.0MB |
| HEAP | FLOW_NETWORK | 1.65ms | 205.8MB |
| ORDERED_MAP | COO | 1.65ms | 210.1MB |
| PERSISTENT_TREE | DYNAMIC_ADJ_LIST | 1.65ms | 206.5MB |
| LINKED_LIST | HYPEREDGE_SET | 1.66ms | 210.4MB |
| TREE_GRAPH_HYBRID | BIDIR_WRAPPER | 1.66ms | 209.8MB |
| AVL_TREE | OCTREE | 1.66ms | 207.0MB |
| BITSET_DYNAMIC | WEIGHTED_GRAPH | 1.66ms | 206.2MB |
| RED_BLACK_TREE | FLOW_NETWORK | 1.66ms | 207.0MB |
| ORDERED_MAP_BALANCED | FLOW_NETWORK | 1.67ms | 210.3MB |
| SKIP_LIST | HYPEREDGE_SET | 1.67ms | 206.9MB |
| AHO_CORASICK | BIDIR_WRAPPER | 1.67ms | 206.8MB |
| PATRICIA | DYNAMIC_ADJ_LIST | 1.67ms | 210.9MB |
| HYPERLOGLOG | CSC | 1.68ms | 206.9MB |
| B_PLUS_TREE | None | 1.68ms | 206.4MB |
| TRIE | None | 1.68ms | 210.7MB |
| RADIX_TRIE | TREE_GRAPH_BASIC | 1.68ms | 210.8MB |
| UNION_FIND | CSR | 1.68ms | 206.6MB |
| BITMAP | OCTREE | 1.68ms | 206.2MB |
| LSM_TREE | CSR | 1.69ms | 206.4MB |
| SUFFIX_ARRAY | BLOCK_ADJ_MATRIX | 1.69ms | 206.7MB |
| SPARSE_MATRIX | BLOCK_ADJ_MATRIX | 1.69ms | 206.3MB |
| SPLAY_TREE | CSC | 1.70ms | 207.1MB |
| SEGMENT_TREE | BIDIR_WRAPPER | 1.70ms | 206.6MB |
| TREAP | EDGE_PROPERTY_STORE | 1.71ms | 207.0MB |
| FENWICK_TREE | TEMPORAL_EDGESET | 1.71ms | 206.7MB |
| ADJACENCY_LIST | QUADTREE | 1.71ms | 206.3MB |
| COW_TREE | CSC | 1.73ms | 206.5MB |
| ROARING_BITMAP | BLOCK_ADJ_MATRIX | 1.74ms | 206.2MB |
| SET_TREE | None | 1.74ms | 205.9MB |
| BLOOM_FILTER | None | 1.75ms | 206.0MB |
| SET_HASH | FLOW_NETWORK | 1.75ms | 205.9MB |

## Key Findings

1. **Edge Storage Impact:**
   - Average time with No Edges: 1.90ms
   - Average time with Edges: 1.84ms
   - Overhead: -2.8%

2. **Top 10 Node Modes (Average Performance Across All Edge Modes):**
   1. STACK: 1.71ms average (19 edge combinations tested)
   2. DEQUE: 1.71ms average (19 edge combinations tested)
   3. QUEUE: 1.73ms average (19 edge combinations tested)
   4. ORDERED_MAP: 1.75ms average (19 edge combinations tested)
   5. PERSISTENT_TREE: 1.76ms average (19 edge combinations tested)
   6. B_TREE: 1.76ms average (19 edge combinations tested)
   7. PRIORITY_QUEUE: 1.77ms average (19 edge combinations tested)
   8. SET_TREE: 1.77ms average (19 edge combinations tested)
   9. ARRAY_LIST: 1.78ms average (19 edge combinations tested)
   10. CUCKOO_HASH: 1.79ms average (19 edge combinations tested)

3. **Fastest Configuration:** CUCKOO_HASH+CSR
   - Time: 1.60ms
   - Memory: 206.1MB

4. **Top 10 Edge Modes (Average Performance Across All Node Modes):**
   1. FLOW_NETWORK: 1.81ms average (40 node combinations tested)
   2. CSR: 1.81ms average (40 node combinations tested)
   3. COO: 1.82ms average (40 node combinations tested)
   4. BIDIR_WRAPPER: 1.82ms average (40 node combinations tested)
   5. TEMPORAL_EDGESET: 1.82ms average (40 node combinations tested)
   6. OCTREE: 1.83ms average (40 node combinations tested)
   7. HYPEREDGE_SET: 1.83ms average (40 node combinations tested)
   8. WEIGHTED_GRAPH: 1.84ms average (40 node combinations tested)
   9. QUADTREE: 1.84ms average (40 node combinations tested)
   10. DYNAMIC_ADJ_LIST: 1.85ms average (40 node combinations tested)

## Bottom 20 Slowest Configurations

| Rank | Configuration | Node Mode | Edge Mode | Total Time | Memory |
|------|---------------|-----------|-----------|------------|--------|
| 741 | HYPERLOGLOG+QUADTREE | HYPERLOGLOG | QUADTREE | 2.33ms | 206.9MB |
| 742 | ORDERED_MAP_BALANCED+ADJ_MATRIX | ORDERED_MAP_BALANCED | ADJ_MATRIX | 2.34ms | 210.2MB |
| 743 | TREAP+BLOCK_ADJ_MATRIX | TREAP | BLOCK_ADJ_MATRIX | 2.35ms | 207.0MB |
| 744 | HASH_MAP+ADJ_MATRIX | HASH_MAP | ADJ_MATRIX | 2.37ms | 209.9MB |
| 745 | AVL_TREE+TEMPORAL_EDGESET | AVL_TREE | TEMPORAL_EDGESET | 2.37ms | 207.0MB |
| 746 | SEGMENT_TREE+QUADTREE | SEGMENT_TREE | QUADTREE | 2.38ms | 206.7MB |
| 747 | ROARING_BITMAP+R_TREE | ROARING_BITMAP | R_TREE | 2.40ms | 206.2MB |
| 748 | RED_BLACK_TREE+ADJ_MATRIX | RED_BLACK_TREE | ADJ_MATRIX | 2.44ms | 206.9MB |
| 749 | TREAP+NEURAL_GRAPH | TREAP | NEURAL_GRAPH | 2.45ms | 207.1MB |
| 750 | AVL_TREE+TREE_GRAPH_BASIC | AVL_TREE | TREE_GRAPH_BASIC | 2.47ms | 207.0MB |
| 751 | COUNT_MIN_SKETCH+BLOCK_ADJ_MATRIX | COUNT_MIN_SKETCH | BLOCK_ADJ_MATRIX | 2.50ms | 206.8MB |
| 752 | FENWICK_TREE+CSC | FENWICK_TREE | CSC | 2.56ms | 206.7MB |
| 753 | SPLAY_TREE+EDGE_PROPERTY_STORE | SPLAY_TREE | EDGE_PROPERTY_STORE | 2.59ms | 206.9MB |
| 754 | AHO_CORASICK+ADJ_MATRIX | AHO_CORASICK | ADJ_MATRIX | 2.60ms | 206.8MB |
| 755 | AHO_CORASICK+CSC | AHO_CORASICK | CSC | 2.62ms | 206.8MB |
| 756 | RED_BLACK_TREE+DYNAMIC_ADJ_LIST | RED_BLACK_TREE | DYNAMIC_ADJ_LIST | 2.88ms | 206.9MB |
| 757 | RED_BLACK_TREE+ADJ_LIST | RED_BLACK_TREE | ADJ_LIST | 3.49ms | 206.9MB |
| 758 | AHO_CORASICK+BLOCK_ADJ_MATRIX | AHO_CORASICK | BLOCK_ADJ_MATRIX | 3.63ms | 206.8MB |
| 759 | RED_BLACK_TREE+TREE_GRAPH_BASIC | RED_BLACK_TREE | TREE_GRAPH_BASIC | 3.64ms | 206.9MB |
| 760 | RED_BLACK_TREE+None | RED_BLACK_TREE | None | 4.05ms | 206.9MB |

## Complete Statistics

- **Total Configurations Tested:** 760
- **Fastest:** CUCKOO_HASH+CSR at 1.60ms
- **Slowest:** RED_BLACK_TREE+None at 4.05ms
- **Performance Range:** 2.45ms
- **Speed Difference:** 153.1% slower (slowest vs fastest)
