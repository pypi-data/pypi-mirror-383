# Entity Database Benchmark Results - 10x COMPLEXITY

## Configuration

- **Total Entities:** 10000
  - Users: 5000
  - Posts: 3000
  - Comments: 2000
- **Total Relationships:** 10000
- **Total Operations:** ~50,000+
- **Scale:** 10x compared to base benchmark

## Results Summary

| DB Type | Node Mode | Edge Mode | Total Time | Memory | Ops/sec |
|---------|-----------|-----------|------------|--------|---------|
| Query-Optimized | TREE_GRAPH_HYBRID | WEIGHTED_GRAPH | 362.81ms | 244.85MB | 137812 |
| Write-Optimized | LSM_TREE | DYNAMIC_ADJ_LIST | 375.52ms | 225.36MB | 133148 |
| Persistence-Optimized | B_PLUS_TREE | EDGE_PROPERTY_STORE | 377.04ms | 255.10MB | 132611 |
| Read-Optimized | HASH_MAP | None | 380.25ms | 215.28MB | 131492 |
| Memory-Efficient | B_TREE | CSR | 381.97ms | 234.68MB | 130901 |
| XWData-Optimized | HASH_MAP | None | 382.70ms | 265.00MB | 130650 |
