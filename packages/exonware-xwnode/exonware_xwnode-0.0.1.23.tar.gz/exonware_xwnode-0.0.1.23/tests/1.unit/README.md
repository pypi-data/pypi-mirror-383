# Unit Tests (Layer 1)

**Purpose:** Fine-grained component tests - Verify individual classes, functions, and methods in isolation.

**Target Runtime:** < 5 minutes total

## Structure

Unit tests **mirror the source structure**:

```
tests/1.unit/nodes_tests/         → src/exonware/xwnode/nodes/
tests/1.unit/edges_tests/         → src/exonware/xwnode/edges/
tests/1.unit/common_tests/        → src/exonware/xwnode/common/
tests/1.unit/facade_tests/        → src/exonware/xwnode/facade.py
```

## What Belongs Here

- Component-specific tests
- Method-level tests
- Class behavior tests
- Edge case handling
- Error condition tests
- Isolated functionality tests

## What Doesn't Belong Here

- Cross-module integration (use 2.integration)
- High-level workflows (use 0.core)
- External service tests (use 2.integration)
- Production excellence validation (use 3.advance)

## Hierarchical Execution

```
tests/1.unit/runner.py (orchestrator)
├─→ tests/1.unit/nodes_tests/runner.py
│   └─→ tests/1.unit/nodes_tests/strategies_tests/runner.py
├─→ tests/1.unit/edges_tests/runner.py
│   └─→ tests/1.unit/edges_tests/strategies_tests/runner.py
├─→ tests/1.unit/common_tests/runner.py
└─→ tests/1.unit/facade_tests/runner.py
```

## Running Unit Tests

```bash
# All unit tests
python tests/runner.py --unit

# Directly
python tests/1.unit/runner.py

# Specific module
python tests/1.unit/nodes_tests/runner.py

# With pytest
pytest tests/1.unit/ -m xwnode_unit
```

## Test Guidelines

- Use **fakes/mocks** only (no external dependencies)
- Fast execution (< 100ms per test)
- No network/disk I/O (except local tmp_path)
- Isolated tests (no dependencies between tests)
- Module-specific fixtures in subdirectory conftest.py

## Markers

Unit tests should use:
```python
@pytest.mark.xwnode_unit
```

## Adding New Module Tests

1. Create directory mirroring source: `tests/1.unit/module_name_tests/`
2. Add `__init__.py`, `conftest.py`, `runner.py`
3. Add test files: `test_*.py`
4. Module runner will be auto-discovered by orchestrator

## Success Criteria

- ✅ All tests pass (100%)
- ✅ All module runners succeed
- ✅ Total runtime < 5 minutes
- ✅ ≥ 80% coverage
- ✅ No external dependencies

