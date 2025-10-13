# Core Tests (Layer 0)

**Purpose:** 20% tests for 80% value - Fast, high-value checks covering critical functionality.

**Target Runtime:** < 30 seconds total

## What Belongs Here

- Critical path tests
- High-value integration tests
- Fast-running functionality checks
- Basic security validations
- Core operation verification

## What Doesn't Belong Here

- Slow tests (> 1 second per test)
- Detailed component tests (use 1.unit)
- Scenario-based tests (use 2.integration)
- Edge case tests (use 1.unit)

## Current Tests

- `test_all_node_strategies.py` - 47 tests covering all 28 node strategies
- `test_all_edge_strategies.py` - 34 tests covering all 16 edge strategies  
- `test_security_all_strategies.py` - Security validation tests
- `test_facade.py` - Facade pattern tests
- `test_errors.py` - Error handling tests
- Various individual strategy tests

## Running Core Tests

```bash
# Via main orchestrator
python tests/runner.py --core

# Directly
python tests/0.core/runner.py

# With pytest
pytest tests/0.core/ -m xwnode_core
```

## Test Data

Test data is organized in `data/` subdirectory:
- `inputs/` - Input test data files
- `expected/` - Expected output files
- `fixtures/` - Reusable test fixtures

## Markers

Core tests should use:
```python
@pytest.mark.xwnode_core
```

## Success Criteria

- ✅ All tests pass (100%)
- ✅ Total runtime < 30 seconds
- ✅ Fails fast on fundamental issues
- ✅ Covers critical user workflows

