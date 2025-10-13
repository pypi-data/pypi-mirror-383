# Entity Database Benchmark Results

## Configuration

- **Total Entities:** 1000 (500 users, 300 posts, 200 comments)
- **Total Relationships:** 1000 (user follows)
- **Operations:** Insert, View, Update (50%), Soft Delete, Hard Delete, Search, List
- **Database Types:** 6 (Read-Optimized, Write-Optimized, Memory-Efficient, Query-Optimized, Persistence-Optimized, XWData-Optimized)

## Results Summary

| DB Type | Node Mode | Edge Mode | Total Time | Memory | Best For |
|---------|-----------|-----------|------------|--------|----------|
| Memory-Efficient | B_TREE | CSR | 12.24ms | 207.82MB | Large datasets |
| Write-Optimized | LSM_TREE | DYNAMIC_ADJ_LIST | 12.25ms | 206.71MB | High throughput |
| Read-Optimized | HASH_MAP | None | 12.51ms | 205.57MB | Fast lookups |
| Persistence-Optimized | B_PLUS_TREE | EDGE_PROPERTY_STORE | 13.09ms | 209.80MB | Durability |
| Query-Optimized | TREE_GRAPH_HYBRID | WEIGHTED_GRAPH | 13.35ms | 208.81MB | Graph traversal |
| XWData-Optimized | HASH_MAP | None | 13.87ms | 210.80MB | Data interchange |

## Detailed Performance Breakdown

### Memory-Efficient Database

**Configuration:**
- Node Strategy: `B_TREE`
- Edge Strategy: `CSR`
- Total Time: 12.24 ms
- Peak Memory: 207.82 MB

**Operation Performance:**

| Operation | Count | Total Time | Avg Time | Min Time | Max Time |
|-----------|-------|------------|----------|----------|----------|
| insert_user | 1 | 2.20ms | 2.1954ms | 2.1954ms | 2.1954ms |
| insert_post | 1 | 1.51ms | 1.5133ms | 1.5133ms | 1.5133ms |
| insert_comment | 1 | 1.02ms | 1.0241ms | 1.0241ms | 1.0241ms |
| insert_relationship | 1 | 4.68ms | 4.6826ms | 4.6826ms | 4.6826ms |
| read_user | 1 | 0.07ms | 0.0717ms | 0.0717ms | 0.0717ms |
| read_post | 1 | 0.10ms | 0.0963ms | 0.0963ms | 0.0963ms |
| read_comment | 1 | 0.06ms | 0.0621ms | 0.0621ms | 0.0621ms |
| update_user | 1 | 0.12ms | 0.1151ms | 0.1151ms | 0.1151ms |
| update_post | 1 | 0.03ms | 0.0282ms | 0.0282ms | 0.0282ms |
| update_comment | 1 | 0.03ms | 0.0338ms | 0.0338ms | 0.0338ms |
| soft_delete_comment | 1 | 0.01ms | 0.0075ms | 0.0075ms | 0.0075ms |
| search_users | 1 | 0.31ms | 0.3074ms | 0.3074ms | 0.3074ms |
| list_posts_by_user | 1 | 0.03ms | 0.0262ms | 0.0262ms | 0.0262ms |
| list_comments_by_post | 1 | 0.02ms | 0.0210ms | 0.0210ms | 0.0210ms |
| list_all_users | 1 | 0.01ms | 0.0068ms | 0.0068ms | 0.0068ms |
| query_followers | 1 | 1.05ms | 1.0506ms | 1.0506ms | 1.0506ms |
| query_following | 1 | 0.97ms | 0.9747ms | 0.9747ms | 0.9747ms |
| hard_delete_comment | 1 | 0.01ms | 0.0109ms | 0.0109ms | 0.0109ms |
| hard_delete_post | 1 | 0.01ms | 0.0074ms | 0.0074ms | 0.0074ms |
| hard_delete_user | 1 | 0.01ms | 0.0075ms | 0.0075ms | 0.0075ms |

### Write-Optimized Database

**Configuration:**
- Node Strategy: `LSM_TREE`
- Edge Strategy: `DYNAMIC_ADJ_LIST`
- Total Time: 12.25 ms
- Peak Memory: 206.71 MB

**Operation Performance:**

| Operation | Count | Total Time | Avg Time | Min Time | Max Time |
|-----------|-------|------------|----------|----------|----------|
| insert_user | 1 | 2.38ms | 2.3827ms | 2.3827ms | 2.3827ms |
| insert_post | 1 | 1.44ms | 1.4362ms | 1.4362ms | 1.4362ms |
| insert_comment | 1 | 1.11ms | 1.1102ms | 1.1102ms | 1.1102ms |
| insert_relationship | 1 | 4.41ms | 4.4120ms | 4.4120ms | 4.4120ms |
| read_user | 1 | 0.07ms | 0.0709ms | 0.0709ms | 0.0709ms |
| read_post | 1 | 0.09ms | 0.0854ms | 0.0854ms | 0.0854ms |
| read_comment | 1 | 0.05ms | 0.0513ms | 0.0513ms | 0.0513ms |
| update_user | 1 | 0.09ms | 0.0885ms | 0.0885ms | 0.0885ms |
| update_post | 1 | 0.03ms | 0.0340ms | 0.0340ms | 0.0340ms |
| update_comment | 1 | 0.03ms | 0.0332ms | 0.0332ms | 0.0332ms |
| soft_delete_comment | 1 | 0.01ms | 0.0083ms | 0.0083ms | 0.0083ms |
| search_users | 1 | 0.34ms | 0.3419ms | 0.3419ms | 0.3419ms |
| list_posts_by_user | 1 | 0.05ms | 0.0454ms | 0.0454ms | 0.0454ms |
| list_comments_by_post | 1 | 0.03ms | 0.0338ms | 0.0338ms | 0.0338ms |
| list_all_users | 1 | 0.01ms | 0.0117ms | 0.0117ms | 0.0117ms |
| query_followers | 1 | 1.09ms | 1.0872ms | 1.0872ms | 1.0872ms |
| query_following | 1 | 0.99ms | 0.9906ms | 0.9906ms | 0.9906ms |
| hard_delete_comment | 1 | 0.01ms | 0.0094ms | 0.0094ms | 0.0094ms |
| hard_delete_post | 1 | 0.01ms | 0.0085ms | 0.0085ms | 0.0085ms |
| hard_delete_user | 1 | 0.01ms | 0.0076ms | 0.0076ms | 0.0076ms |

### Read-Optimized Database

**Configuration:**
- Node Strategy: `HASH_MAP`
- Edge Strategy: `None`
- Total Time: 12.51 ms
- Peak Memory: 205.57 MB

**Operation Performance:**

| Operation | Count | Total Time | Avg Time | Min Time | Max Time |
|-----------|-------|------------|----------|----------|----------|
| insert_user | 1 | 2.49ms | 2.4853ms | 2.4853ms | 2.4853ms |
| insert_post | 1 | 1.48ms | 1.4760ms | 1.4760ms | 1.4760ms |
| insert_comment | 1 | 0.94ms | 0.9382ms | 0.9382ms | 0.9382ms |
| insert_relationship | 1 | 4.62ms | 4.6228ms | 4.6228ms | 4.6228ms |
| read_user | 1 | 0.10ms | 0.0957ms | 0.0957ms | 0.0957ms |
| read_post | 1 | 0.05ms | 0.0544ms | 0.0544ms | 0.0544ms |
| read_comment | 1 | 0.05ms | 0.0458ms | 0.0458ms | 0.0458ms |
| update_user | 1 | 0.08ms | 0.0758ms | 0.0758ms | 0.0758ms |
| update_post | 1 | 0.03ms | 0.0292ms | 0.0292ms | 0.0292ms |
| update_comment | 1 | 0.04ms | 0.0402ms | 0.0402ms | 0.0402ms |
| soft_delete_comment | 1 | 0.01ms | 0.0132ms | 0.0132ms | 0.0132ms |
| search_users | 1 | 0.32ms | 0.3181ms | 0.3181ms | 0.3181ms |
| list_posts_by_user | 1 | 0.05ms | 0.0458ms | 0.0458ms | 0.0458ms |
| list_comments_by_post | 1 | 0.04ms | 0.0416ms | 0.0416ms | 0.0416ms |
| list_all_users | 1 | 0.01ms | 0.0116ms | 0.0116ms | 0.0116ms |
| query_followers | 1 | 1.17ms | 1.1677ms | 1.1677ms | 1.1677ms |
| query_following | 1 | 1.01ms | 1.0147ms | 1.0147ms | 1.0147ms |
| hard_delete_comment | 1 | 0.02ms | 0.0168ms | 0.0168ms | 0.0168ms |
| hard_delete_post | 1 | 0.01ms | 0.0099ms | 0.0099ms | 0.0099ms |
| hard_delete_user | 1 | 0.01ms | 0.0103ms | 0.0103ms | 0.0103ms |

### Persistence-Optimized Database

**Configuration:**
- Node Strategy: `B_PLUS_TREE`
- Edge Strategy: `EDGE_PROPERTY_STORE`
- Total Time: 13.09 ms
- Peak Memory: 209.80 MB

**Operation Performance:**

| Operation | Count | Total Time | Avg Time | Min Time | Max Time |
|-----------|-------|------------|----------|----------|----------|
| insert_user | 1 | 2.63ms | 2.6332ms | 2.6332ms | 2.6332ms |
| insert_post | 1 | 1.86ms | 1.8607ms | 1.8607ms | 1.8607ms |
| insert_comment | 1 | 0.98ms | 0.9819ms | 0.9819ms | 0.9819ms |
| insert_relationship | 1 | 4.54ms | 4.5416ms | 4.5416ms | 4.5416ms |
| read_user | 1 | 0.04ms | 0.0388ms | 0.0388ms | 0.0388ms |
| read_post | 1 | 0.04ms | 0.0436ms | 0.0436ms | 0.0436ms |
| read_comment | 1 | 0.04ms | 0.0367ms | 0.0367ms | 0.0367ms |
| update_user | 1 | 0.07ms | 0.0715ms | 0.0715ms | 0.0715ms |
| update_post | 1 | 0.03ms | 0.0253ms | 0.0253ms | 0.0253ms |
| update_comment | 1 | 0.03ms | 0.0259ms | 0.0259ms | 0.0259ms |
| soft_delete_comment | 1 | 0.01ms | 0.0072ms | 0.0072ms | 0.0072ms |
| search_users | 1 | 0.30ms | 0.3047ms | 0.3047ms | 0.3047ms |
| list_posts_by_user | 1 | 0.02ms | 0.0248ms | 0.0248ms | 0.0248ms |
| list_comments_by_post | 1 | 0.02ms | 0.0226ms | 0.0226ms | 0.0226ms |
| list_all_users | 1 | 0.01ms | 0.0061ms | 0.0061ms | 0.0061ms |
| query_followers | 1 | 1.21ms | 1.2128ms | 1.2128ms | 1.2128ms |
| query_following | 1 | 1.20ms | 1.2041ms | 1.2041ms | 1.2041ms |
| hard_delete_comment | 1 | 0.02ms | 0.0207ms | 0.0207ms | 0.0207ms |
| hard_delete_post | 1 | 0.02ms | 0.0168ms | 0.0168ms | 0.0168ms |
| hard_delete_user | 1 | 0.02ms | 0.0160ms | 0.0160ms | 0.0160ms |

### Query-Optimized Database

**Configuration:**
- Node Strategy: `TREE_GRAPH_HYBRID`
- Edge Strategy: `WEIGHTED_GRAPH`
- Total Time: 13.35 ms
- Peak Memory: 208.81 MB

**Operation Performance:**

| Operation | Count | Total Time | Avg Time | Min Time | Max Time |
|-----------|-------|------------|----------|----------|----------|
| insert_user | 1 | 2.49ms | 2.4859ms | 2.4859ms | 2.4859ms |
| insert_post | 1 | 1.96ms | 1.9649ms | 1.9649ms | 1.9649ms |
| insert_comment | 1 | 1.54ms | 1.5436ms | 1.5436ms | 1.5436ms |
| insert_relationship | 1 | 4.69ms | 4.6884ms | 4.6884ms | 4.6884ms |
| read_user | 1 | 0.05ms | 0.0481ms | 0.0481ms | 0.0481ms |
| read_post | 1 | 0.05ms | 0.0500ms | 0.0500ms | 0.0500ms |
| read_comment | 1 | 0.04ms | 0.0411ms | 0.0411ms | 0.0411ms |
| update_user | 1 | 0.09ms | 0.0879ms | 0.0879ms | 0.0879ms |
| update_post | 1 | 0.03ms | 0.0260ms | 0.0260ms | 0.0260ms |
| update_comment | 1 | 0.03ms | 0.0282ms | 0.0282ms | 0.0282ms |
| soft_delete_comment | 1 | 0.01ms | 0.0079ms | 0.0079ms | 0.0079ms |
| search_users | 1 | 0.30ms | 0.2965ms | 0.2965ms | 0.2965ms |
| list_posts_by_user | 1 | 0.02ms | 0.0248ms | 0.0248ms | 0.0248ms |
| list_comments_by_post | 1 | 0.02ms | 0.0235ms | 0.0235ms | 0.0235ms |
| list_all_users | 1 | 0.01ms | 0.0061ms | 0.0061ms | 0.0061ms |
| query_followers | 1 | 1.02ms | 1.0174ms | 1.0174ms | 1.0174ms |
| query_following | 1 | 0.98ms | 0.9827ms | 0.9827ms | 0.9827ms |
| hard_delete_comment | 1 | 0.01ms | 0.0089ms | 0.0089ms | 0.0089ms |
| hard_delete_post | 1 | 0.01ms | 0.0074ms | 0.0074ms | 0.0074ms |
| hard_delete_user | 1 | 0.01ms | 0.0073ms | 0.0073ms | 0.0073ms |

### XWData-Optimized Database

**Configuration:**
- Node Strategy: `HASH_MAP`
- Edge Strategy: `None`
- Total Time: 13.87 ms
- Peak Memory: 210.80 MB

**Operation Performance:**

| Operation | Count | Total Time | Avg Time | Min Time | Max Time |
|-----------|-------|------------|----------|----------|----------|
| insert_user | 1 | 2.66ms | 2.6625ms | 2.6625ms | 2.6625ms |
| insert_post | 1 | 1.60ms | 1.6045ms | 1.6045ms | 1.6045ms |
| insert_comment | 1 | 1.27ms | 1.2663ms | 1.2663ms | 1.2663ms |
| insert_relationship | 1 | 4.09ms | 4.0904ms | 4.0904ms | 4.0904ms |
| read_user | 1 | 0.12ms | 0.1232ms | 0.1232ms | 0.1232ms |
| read_post | 1 | 0.09ms | 0.0870ms | 0.0870ms | 0.0870ms |
| read_comment | 1 | 0.05ms | 0.0548ms | 0.0548ms | 0.0548ms |
| update_user | 1 | 0.13ms | 0.1265ms | 0.1265ms | 0.1265ms |
| update_post | 1 | 0.04ms | 0.0375ms | 0.0375ms | 0.0375ms |
| update_comment | 1 | 0.05ms | 0.0482ms | 0.0482ms | 0.0482ms |
| soft_delete_comment | 1 | 0.01ms | 0.0098ms | 0.0098ms | 0.0098ms |
| search_users | 1 | 0.35ms | 0.3520ms | 0.3520ms | 0.3520ms |
| list_posts_by_user | 1 | 0.04ms | 0.0383ms | 0.0383ms | 0.0383ms |
| list_comments_by_post | 1 | 0.03ms | 0.0347ms | 0.0347ms | 0.0347ms |
| list_all_users | 1 | 0.01ms | 0.0112ms | 0.0112ms | 0.0112ms |
| query_followers | 1 | 1.43ms | 1.4326ms | 1.4326ms | 1.4326ms |
| query_following | 1 | 1.81ms | 1.8056ms | 1.8056ms | 1.8056ms |
| hard_delete_comment | 1 | 0.05ms | 0.0483ms | 0.0483ms | 0.0483ms |
| hard_delete_post | 1 | 0.01ms | 0.0146ms | 0.0146ms | 0.0146ms |
| hard_delete_user | 1 | 0.02ms | 0.0245ms | 0.0245ms | 0.0245ms |

## Recommendations

Based on the benchmark results:

- **Fastest Overall:** Memory-Efficient - Best for latency-sensitive applications
- **Most Memory Efficient:** Read-Optimized - Best for large-scale deployments

## Notes

- All benchmarks run on the same hardware and software environment
- Times are measured in milliseconds (ms)
- Memory is measured in megabytes (MB)
- Operations include all CRUD operations plus search and relationship queries
