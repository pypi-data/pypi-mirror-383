# Exhaustive Strategy Search Results - 10x COMPLEXITY

## Test Configuration

- **Total Combinations Tested:** 760
- **Scale:** 10x complexity
- **Dataset:** 5000 users, 3000 posts, 2000 comments, 10000 relationships
- **Total Entities:** 20000
- **Operations:** Insert, Read (1000), Update (5000), Relationship queries (1000)

## Predictions (10x Scale)

### 10X Scale
- **Predicted Winner:** B_TREE + ADJ_LIST
- **Reasoning:** B_TREE cache hits dominate at scale, ADJ_LIST is sparse-efficient
- **Estimated Time:** 350.0ms

### Dark Horse
- **Predicted Winner:** CUCKOO_HASH + CSR
- **Reasoning:** 1x champion might scale well, CSR compression helps
- **Estimated Time:** 340.0ms

### Wildcard
- **Predicted Winner:** LSM_TREE + DYNAMIC_ADJ_LIST
- **Reasoning:** Write-optimized should dominate with 20K inserts
- **Estimated Time:** 330.0ms

## Top 20 Fastest Configurations

| Rank | Configuration | Node Mode | Edge Mode | Total Time | Memory | Ops/sec |
|------|---------------|-----------|-----------|------------|--------|----------|
| 1 [1st] | ROARING_BITMAP+TREE_GRAPH_BASIC | ROARING_BITMAP | TREE_GRAPH_BASIC | 277.33ms | 216.6MB | 180292 |
| 2 [2nd] | HASH_MAP+FLOW_NETWORK | HASH_MAP | FLOW_NETWORK | 278.59ms | 216.4MB | 179474 |
| 3 [3rd] | TREE_GRAPH_HYBRID+TEMPORAL_EDGESET | TREE_GRAPH_HYBRID | TEMPORAL_EDGESET | 278.64ms | 216.2MB | 179443 |
| 4  | HASH_MAP+OCTREE | HASH_MAP | OCTREE | 278.86ms | 216.3MB | 179305 |
| 5  | TRIE+NEURAL_GRAPH | TRIE | NEURAL_GRAPH | 279.13ms | 216.2MB | 179127 |
| 6  | LINKED_LIST+WEIGHTED_GRAPH | LINKED_LIST | WEIGHTED_GRAPH | 279.17ms | 216.1MB | 179104 |
| 7  | CUCKOO_HASH+WEIGHTED_GRAPH | CUCKOO_HASH | WEIGHTED_GRAPH | 279.82ms | 216.5MB | 178687 |
| 8  | SET_TREE+TREE_GRAPH_BASIC | SET_TREE | TREE_GRAPH_BASIC | 279.98ms | 216.3MB | 178582 |
| 9  | TREE_GRAPH_HYBRID+WEIGHTED_GRAPH | TREE_GRAPH_HYBRID | WEIGHTED_GRAPH | 280.06ms | 216.3MB | 178532 |
| 10  | TRIE+R_TREE | TRIE | R_TREE | 280.51ms | 215.4MB | 178248 |
| 11  | BITMAP+EDGE_PROPERTY_STORE | BITMAP | EDGE_PROPERTY_STORE | 280.63ms | 216.5MB | 178168 |
| 12  | BLOOM_FILTER+QUADTREE | BLOOM_FILTER | QUADTREE | 280.70ms | 216.4MB | 178127 |
| 13  | RADIX_TRIE+ADJ_LIST | RADIX_TRIE | ADJ_LIST | 281.41ms | 216.2MB | 177677 |
| 14  | TREE_GRAPH_HYBRID+QUADTREE | TREE_GRAPH_HYBRID | QUADTREE | 281.61ms | 216.3MB | 177553 |
| 15  | BITMAP+COO | BITMAP | COO | 281.73ms | 216.5MB | 177472 |
| 16  | PATRICIA+DYNAMIC_ADJ_LIST | PATRICIA | DYNAMIC_ADJ_LIST | 281.84ms | 216.2MB | 177405 |
| 17  | HASH_MAP+DYNAMIC_ADJ_LIST | HASH_MAP | DYNAMIC_ADJ_LIST | 282.07ms | 216.3MB | 177262 |
| 18  | PRIORITY_QUEUE+COO | PRIORITY_QUEUE | COO | 282.78ms | 215.6MB | 176818 |
| 19  | SET_HASH+EDGE_PROPERTY_STORE | SET_HASH | EDGE_PROPERTY_STORE | 283.00ms | 216.3MB | 176676 |
| 20  | BLOOM_FILTER+ADJ_LIST | BLOOM_FILTER | ADJ_LIST | 283.04ms | 216.4MB | 176650 |

## Top 20 Most Memory Efficient

| Rank | Configuration | Node Mode | Edge Mode | Memory | Total Time |
|------|---------------|-----------|-----------|--------|------------|
| 1 | TRIE+R_TREE | TRIE | R_TREE | 215.4MB | 280.51ms |
| 2 | RADIX_TRIE+WEIGHTED_GRAPH | RADIX_TRIE | WEIGHTED_GRAPH | 215.4MB | 294.17ms |
| 3 | TRIE+BLOCK_ADJ_MATRIX | TRIE | BLOCK_ADJ_MATRIX | 215.4MB | 298.12ms |
| 4 | HEAP+ADJ_MATRIX | HEAP | ADJ_MATRIX | 215.4MB | 300.07ms |
| 5 | RADIX_TRIE+CSR | RADIX_TRIE | CSR | 215.4MB | 319.66ms |
| 6 | PRIORITY_QUEUE+None | PRIORITY_QUEUE | None | 215.5MB | 292.73ms |
| 7 | QUEUE+HYPEREDGE_SET | QUEUE | HYPEREDGE_SET | 215.5MB | 296.74ms |
| 8 | DEQUE+NEURAL_GRAPH | DEQUE | NEURAL_GRAPH | 215.5MB | 303.55ms |
| 9 | LINKED_LIST+R_TREE | LINKED_LIST | R_TREE | 215.5MB | 313.71ms |
| 10 | DEQUE+TREE_GRAPH_BASIC | DEQUE | TREE_GRAPH_BASIC | 215.5MB | 325.77ms |
| 11 | SET_HASH+TREE_GRAPH_BASIC | SET_HASH | TREE_GRAPH_BASIC | 215.5MB | 287.11ms |
| 12 | LINKED_LIST+NEURAL_GRAPH | LINKED_LIST | NEURAL_GRAPH | 215.5MB | 289.94ms |
| 13 | SET_HASH+BLOCK_ADJ_MATRIX | SET_HASH | BLOCK_ADJ_MATRIX | 215.5MB | 292.20ms |
| 14 | ORDERED_MAP+DYNAMIC_ADJ_LIST | ORDERED_MAP | DYNAMIC_ADJ_LIST | 215.5MB | 325.62ms |
| 15 | ORDERED_MAP_BALANCED+None | ORDERED_MAP_BALANCED | None | 215.5MB | 314.48ms |
| 16 | ARRAY_LIST+COO | ARRAY_LIST | COO | 215.5MB | 318.83ms |
| 17 | SET_TREE+CSR | SET_TREE | CSR | 215.5MB | 294.78ms |
| 18 | STACK+QUADTREE | STACK | QUADTREE | 215.6MB | 335.19ms |
| 19 | ORDERED_MAP_BALANCED+COO | ORDERED_MAP_BALANCED | COO | 215.6MB | 300.94ms |
| 20 | SET_HASH+BIDIR_WRAPPER | SET_HASH | BIDIR_WRAPPER | 215.6MB | 302.43ms |

## Prediction Accuracy

**Predicted Winner:** B_TREE + ADJ_LIST
**Actual Winner:** ROARING_BITMAP+TREE_GRAPH_BASIC
**Prediction Status:** INCORRECT

**Why the difference:**
- Predicted: B_TREE cache hits dominate at scale, ADJ_LIST is sparse-efficient
- Actual winner scaled differently than expected

## Strategy Analysis

### Best Edge Mode for Each Node Mode

| Node Mode | Best Edge Mode | Time | Memory | Ops/sec |
|-----------|----------------|------|--------|----------|
| ROARING_BITMAP | TREE_GRAPH_BASIC | 277.33ms | 216.6MB | 180292 |
| HASH_MAP | FLOW_NETWORK | 278.59ms | 216.4MB | 179474 |
| TREE_GRAPH_HYBRID | TEMPORAL_EDGESET | 278.64ms | 216.2MB | 179443 |
| TRIE | NEURAL_GRAPH | 279.13ms | 216.2MB | 179127 |
| LINKED_LIST | WEIGHTED_GRAPH | 279.17ms | 216.1MB | 179104 |
| CUCKOO_HASH | WEIGHTED_GRAPH | 279.82ms | 216.5MB | 178687 |
| SET_TREE | TREE_GRAPH_BASIC | 279.98ms | 216.3MB | 178582 |
| BITMAP | EDGE_PROPERTY_STORE | 280.63ms | 216.5MB | 178168 |
| BLOOM_FILTER | QUADTREE | 280.70ms | 216.4MB | 178127 |
| RADIX_TRIE | ADJ_LIST | 281.41ms | 216.2MB | 177677 |
| PATRICIA | DYNAMIC_ADJ_LIST | 281.84ms | 216.2MB | 177405 |
| PRIORITY_QUEUE | COO | 282.78ms | 215.6MB | 176818 |
| SET_HASH | EDGE_PROPERTY_STORE | 283.00ms | 216.3MB | 176676 |
| SPARSE_MATRIX | QUADTREE | 283.26ms | 216.6MB | 176519 |
| B_PLUS_TREE | R_TREE | 283.28ms | 216.7MB | 176505 |
| ORDERED_MAP | ADJ_MATRIX | 284.33ms | 216.3MB | 175851 |
| PERSISTENT_TREE | EDGE_PROPERTY_STORE | 284.71ms | 216.7MB | 175620 |
| B_TREE | QUADTREE | 285.32ms | 216.6MB | 175243 |
| HEAP | None | 285.32ms | 216.2MB | 175241 |
| SEGMENT_TREE | WEIGHTED_GRAPH | 285.73ms | 217.2MB | 174987 |
| COW_TREE | ADJ_LIST | 286.86ms | 216.9MB | 174302 |
| ADJACENCY_LIST | ADJ_MATRIX | 286.87ms | 216.7MB | 174292 |
| DEQUE | COO | 287.34ms | 216.2MB | 174012 |
| QUEUE | CSC | 287.73ms | 216.3MB | 173776 |
| SUFFIX_ARRAY | HYPEREDGE_SET | 288.37ms | 216.4MB | 173390 |
| BITSET_DYNAMIC | ADJ_LIST | 288.80ms | 215.8MB | 173133 |
| AHO_CORASICK | TREE_GRAPH_BASIC | 288.96ms | 217.1MB | 173033 |
| ORDERED_MAP_BALANCED | TREE_GRAPH_BASIC | 289.06ms | 216.3MB | 172972 |
| ARRAY_LIST | R_TREE | 289.62ms | 216.3MB | 172639 |
| HYPERLOGLOG | None | 289.68ms | 217.2MB | 172602 |
| TREAP | QUADTREE | 291.11ms | 217.4MB | 171755 |
| SKIP_LIST | ADJ_LIST | 291.40ms | 216.4MB | 171585 |
| UNION_FIND | ADJ_LIST | 292.24ms | 217.2MB | 171094 |
| RED_BLACK_TREE | NEURAL_GRAPH | 292.44ms | 217.4MB | 170975 |
| STACK | CSR | 292.59ms | 216.2MB | 170886 |
| LSM_TREE | BIDIR_WRAPPER | 292.66ms | 216.8MB | 170845 |
| FENWICK_TREE | ADJ_LIST | 292.71ms | 217.2MB | 170815 |
| COUNT_MIN_SKETCH | CSC | 293.03ms | 217.2MB | 170630 |
| SPLAY_TREE | TREE_GRAPH_BASIC | 293.49ms | 216.7MB | 170362 |
| AVL_TREE | NEURAL_GRAPH | 293.49ms | 217.3MB | 170361 |

## Key Findings

1. **Edge Storage Impact at 10x Scale:**
   - Average time with No Edges: 304.08ms
   - Average time with Edges: 303.64ms
   - Overhead: -0.1%

2. **Top 10 Node Modes at 10x Scale (Average Performance):**
   1. TREE_GRAPH_HYBRID: 288.45ms average (173342 ops/sec, 19 edge combos)
   2. HASH_MAP: 294.34ms average (169872 ops/sec, 19 edge combos)
   3. B_PLUS_TREE: 297.11ms average (168288 ops/sec, 19 edge combos)
   4. CUCKOO_HASH: 298.40ms average (167558 ops/sec, 19 edge combos)
   5. PATRICIA: 299.26ms average (167078 ops/sec, 19 edge combos)
   6. BITSET_DYNAMIC: 299.54ms average (166922 ops/sec, 19 edge combos)
   7. BLOOM_FILTER: 299.60ms average (166889 ops/sec, 19 edge combos)
   8. RADIX_TRIE: 300.12ms average (166601 ops/sec, 19 edge combos)
   9. B_TREE: 300.26ms average (166521 ops/sec, 19 edge combos)
   10. ORDERED_MAP: 300.56ms average (166354 ops/sec, 19 edge combos)

3. **Top 10 Edge Modes at 10x Scale (Average Performance):**
   1. ADJ_LIST: 298.05ms average (167759 ops/sec, 40 node combos)
   2. CSR: 300.95ms average (166142 ops/sec, 40 node combos)
   3. EDGE_PROPERTY_STORE: 301.23ms average (165983 ops/sec, 40 node combos)
   4. FLOW_NETWORK: 302.52ms average (165277 ops/sec, 40 node combos)
   5. OCTREE: 302.56ms average (165255 ops/sec, 40 node combos)
   6. R_TREE: 302.93ms average (165055 ops/sec, 40 node combos)
   7. NEURAL_GRAPH: 302.93ms average (165052 ops/sec, 40 node combos)
   8. CSC: 302.94ms average (165050 ops/sec, 40 node combos)
   9. TREE_GRAPH_BASIC: 303.39ms average (164805 ops/sec, 40 node combos)
   10. DYNAMIC_ADJ_LIST: 303.73ms average (164622 ops/sec, 40 node combos)

4. **Champion at 10x Scale:** ROARING_BITMAP+TREE_GRAPH_BASIC
   - Time: 277.33ms
   - Memory: 216.6MB
   - Throughput: 180292 ops/sec


## Bottom 20 Slowest Configurations

| Rank | Configuration | Node Mode | Edge Mode | Total Time | Memory |
|------|---------------|-----------|-----------|------------|--------|
| 741 | TREAP+ADJ_LIST | TREAP | ADJ_LIST | 339.00ms | 217.3MB |
| 742 | RED_BLACK_TREE+HYPEREDGE_SET | RED_BLACK_TREE | HYPEREDGE_SET | 339.29ms | 216.7MB |
| 743 | B_PLUS_TREE+BLOCK_ADJ_MATRIX | B_PLUS_TREE | BLOCK_ADJ_MATRIX | 340.00ms | 216.6MB |
| 744 | HYPERLOGLOG+BLOCK_ADJ_MATRIX | HYPERLOGLOG | BLOCK_ADJ_MATRIX | 340.16ms | 216.6MB |
| 745 | PERSISTENT_TREE+HYPEREDGE_SET | PERSISTENT_TREE | HYPEREDGE_SET | 340.47ms | 216.6MB |
| 746 | SUFFIX_ARRAY+WEIGHTED_GRAPH | SUFFIX_ARRAY | WEIGHTED_GRAPH | 341.42ms | 217.2MB |
| 747 | TRIE+TREE_GRAPH_BASIC | TRIE | TREE_GRAPH_BASIC | 343.26ms | 216.2MB |
| 748 | ORDERED_MAP_BALANCED+R_TREE | ORDERED_MAP_BALANCED | R_TREE | 345.87ms | 216.2MB |
| 749 | SUFFIX_ARRAY+ADJ_MATRIX | SUFFIX_ARRAY | ADJ_MATRIX | 346.65ms | 216.9MB |
| 750 | TRIE+None | TRIE | None | 346.72ms | 216.2MB |
| 751 | TREAP+DYNAMIC_ADJ_LIST | TREAP | DYNAMIC_ADJ_LIST | 347.10ms | 217.4MB |
| 752 | FENWICK_TREE+COO | FENWICK_TREE | COO | 347.52ms | 216.5MB |
| 753 | SEGMENT_TREE+R_TREE | SEGMENT_TREE | R_TREE | 347.62ms | 217.1MB |
| 754 | ARRAY_LIST+BIDIR_WRAPPER | ARRAY_LIST | BIDIR_WRAPPER | 353.74ms | 216.2MB |
| 755 | ADJACENCY_LIST+QUADTREE | ADJACENCY_LIST | QUADTREE | 353.98ms | 216.6MB |
| 756 | ROARING_BITMAP+COO | ROARING_BITMAP | COO | 364.26ms | 216.5MB |
| 757 | LINKED_LIST+None | LINKED_LIST | None | 388.18ms | 215.9MB |
| 758 | ROARING_BITMAP+BIDIR_WRAPPER | ROARING_BITMAP | BIDIR_WRAPPER | 402.07ms | 216.6MB |
| 759 | LINKED_LIST+ADJ_MATRIX | LINKED_LIST | ADJ_MATRIX | 410.24ms | 216.1MB |
| 760 | FENWICK_TREE+QUADTREE | FENWICK_TREE | QUADTREE | 422.27ms | 217.2MB |

## Complete Statistics (10x Scale)

- **Total Configurations Tested:** 760
- **Fastest:** ROARING_BITMAP+TREE_GRAPH_BASIC at 277.33ms
- **Slowest:** FENWICK_TREE+QUADTREE at 422.27ms
- **Performance Range:** 144.94ms
- **Speed Difference:** 52.3% slower (slowest vs fastest)

## Comparison with 1x Scale Winner

**1x Scale Champion:** CUCKOO_HASH + CSR (1.60ms)
**10x Scale Champion:** ROARING_BITMAP+TREE_GRAPH_BASIC (277.33ms)

**CUCKOO_HASH + CSR at 10x:**
- Rank: 209/760
- Time: 294.89ms
- Scaling: 184.3x (for 10x data)
- Still champion? No - dropped to rank 209

