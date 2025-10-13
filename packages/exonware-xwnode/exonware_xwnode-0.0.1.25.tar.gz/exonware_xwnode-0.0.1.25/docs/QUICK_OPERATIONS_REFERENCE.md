# XWQuery Operations Quick Reference

**56 Operations Available** | **All Registered** | **Ready to Use**

## Quick Overview by Category

| Category | Count | Operations |
|----------|-------|------------|
| **CORE** | 6 | SELECT, INSERT, UPDATE, DELETE, CREATE, DROP |
| **FILTERING** | 10 | WHERE, FILTER, LIKE, IN, HAS, BETWEEN, RANGE, TERM, OPTIONAL, VALUES |
| **AGGREGATION** | 9 | COUNT, SUM, AVG, MIN, MAX, DISTINCT, GROUP, HAVING, SUMMARIZE |
| **PROJECTION** | 2 | PROJECT, EXTEND |
| **ORDERING** | 2 | ORDER, BY |
| **GRAPH** | 5 | MATCH, PATH, OUT, IN, RETURN |
| **DATA** | 4 | LOAD, STORE, MERGE, ALTER |
| **ARRAY** | 2 | SLICING, INDEXING |
| **ADVANCED** | 16 | JOIN, UNION, WITH, AGGREGATE, FOREACH, LET, FOR, WINDOW, DESCRIBE, CONSTRUCT, ASK, SUBSCRIBE, SUBSCRIPTION, MUTATION, PIPE, OPTIONS |
| **TOTAL** | **56** | |

## Status Legend

- ✅ **Fully Implemented** - Complete, production-ready
- 🟡 **Registered** - Available, basic implementation
- 🔵 **Ready** - Registered, awaiting enhancement

## How to Use

### In Interactive Console
```bash
cd xwnode/examples/xwnode_console
python run.py
```

Then type queries:
```sql
XWQuery> SELECT * FROM users
XWQuery> COUNT users
XWQuery> WHERE age > 30
```

### Programmatically
```python
from exonware.xwnode import XWNode
from exonware.xwnode.queries.executors.engine import ExecutionEngine

# Setup
node = XWNode(mode='HASH_MAP')
engine = ExecutionEngine()

# Execute any operation
result = engine.execute("SELECT * FROM collection", node)
```

## Operation Examples

### CORE Operations
```sql
SELECT * FROM users                    # Query data
INSERT INTO users (name: "Alice")      # Add record
UPDATE users SET age = 31 WHERE id = 1 # Update record
DELETE FROM users WHERE age < 18       # Remove records
CREATE COLLECTION products             # Create structure
DROP INDEX user_index                  # Remove structure
```

### FILTERING Operations
```sql
WHERE age > 30                         # Filter by condition
FILTER users BY status = "active"      # General filtering
LIKE "John%"                          # Pattern matching
IN [1, 2, 3]                          # Membership test
HAS email                              # Check property exists
BETWEEN 20 AND 40                      # Range check
```

### AGGREGATION Operations
```sql
COUNT users                            # Count records
SUM sales.amount                       # Sum values
AVG users.age                          # Average
MIN prices.value                       # Minimum
MAX scores.points                      # Maximum
DISTINCT users.city                    # Unique values
GROUP BY department                    # Group records
HAVING count > 5                       # Filter groups
SUMMARIZE sales BY region              # Generate summary
```

### Advanced Operations
```sql
JOIN users WITH orders ON user_id      # Join datasets
UNION users, customers                 # Combine sets
WITH temp AS (SELECT ...) ...          # CTE
AGGREGATE sum, avg, count              # Multiple aggregates
```

## All 56 Operations - Complete List

### 1-6: CORE
1. SELECT ✅
2. INSERT 🟡
3. UPDATE 🟡
4. DELETE 🟡
5. CREATE 🟡
6. DROP 🟡

### 7-16: FILTERING
7. WHERE 🟡
8. FILTER 🟡
9. LIKE 🟡
10. IN 🟡
11. HAS 🟡
12. BETWEEN 🟡
13. RANGE 🟡
14. TERM 🟡
15. OPTIONAL 🟡
16. VALUES 🟡

### 17-25: AGGREGATION
17. COUNT 🟡
18. SUM 🟡
19. AVG 🟡
20. MIN 🟡
21. MAX 🟡
22. DISTINCT 🟡
23. GROUP 🟡
24. HAVING 🟡
25. SUMMARIZE 🟡

### 26-27: PROJECTION
26. PROJECT 🟡
27. EXTEND 🟡

### 28-29: ORDERING
28. ORDER 🟡
29. BY 🟡

### 30-34: GRAPH
30. MATCH 🟡
31. PATH 🟡
32. OUT 🟡
33. IN 🟡
34. RETURN 🟡

### 35-38: DATA
35. LOAD 🟡
36. STORE 🟡
37. MERGE 🟡
38. ALTER 🟡

### 39-40: ARRAY
39. SLICING 🟡
40. INDEXING 🟡

### 41-56: ADVANCED
41. JOIN 🟡
42. UNION 🟡
43. WITH (CTE) 🟡
44. AGGREGATE 🟡
45. FOREACH 🟡
46. LET 🟡
47. FOR 🟡
48. WINDOW 🟡
49. DESCRIBE 🟡
50. CONSTRUCT 🟡
51. ASK 🟡
52. SUBSCRIBE 🟡
53. SUBSCRIPTION 🟡
54. MUTATION 🟡
55. PIPE 🟡
56. OPTIONS 🟡

## Next Steps

Each operation marked with 🟡 is registered and can be invoked, but may need implementation enhancement for full functionality. The SELECT operation ✅ demonstrates the complete implementation pattern.

To contribute to implementation:
1. Choose an operation from the list
2. Review the existing executor in `src/exonware/xwnode/queries/executors/`
3. Enhance the `_do_execute` method with full logic
4. Add tests in `tests/`
5. Update documentation

---

**All 56 operations are now available for use!** 🎉

