# Breadcrumb Performance Test Suite

Automated performance benchmarks for the Breadcrumb AI Tracer.

## Quick Start

```bash
# Run all performance tests
pytest tests/performance/ -v

# Run specific test suite
pytest tests/performance/test_overhead.py -v
pytest tests/performance/test_query_speed.py -v
pytest tests/performance/test_storage_efficiency.py -v

# Skip performance tests (for quick CI)
pytest -m "not performance"

# Run only performance tests
pytest -m performance -v
```

## Test Suites

### 1. Overhead Tests (`test_overhead.py`)

Measures PEP 669 instrumentation overhead across different workload types.

**Tests:**
- Simple function overhead
- Nested function overhead
- Complex function overhead (with actual work)
- Async function overhead
- Overall overhead summary

**Key Metrics:**
- Baseline execution time (no tracing)
- Traced execution time (with PEP 669)
- Overhead percentage

**Expected Results:**
- Complex functions: <500% overhead
- Async functions: <10% overhead
- Simple functions: High overhead expected (measurement artifact)

### 2. Query Speed Tests (`test_query_speed.py`)

Measures database query performance with realistic trace data (5-10K events).

**Tests:**
- Single trace query (<100ms target)
- Recent traces query (<100ms target)
- Aggregation query (<1s target)
- Complex join query (<1s target)
- Find exceptions query (<1s target)
- Analyze performance query (<1s target)

**Key Metrics:**
- Average query time
- P95 query time
- Max query time

**Expected Results:**
- Single trace: ~2-5ms (40x faster than target)
- Aggregations: ~10-50ms (20x faster than target)

### 3. Storage Efficiency Tests (`test_storage_efficiency.py`)

Measures database storage size for different trace scenarios.

**Tests:**
- Simple function calls (minimal data)
- Complex function calls (realistic data)
- Scaling test (100, 500, 1000 calls)
- Compression effectiveness

**Key Metrics:**
- Database size (bytes)
- Bytes per function call
- MB per 1000 calls

**Expected Results:**
- Simple calls: ~0.01 MB per 1K calls
- Complex calls: ~0.05 MB per 1K calls
- Target: <10 MB per 1K calls (1000x better)

## Performance Targets

| Metric | Target | Typical Actual | Status |
|--------|--------|----------------|--------|
| PEP 669 Overhead (Complex) | <500% | ~438% | ✅ PASS |
| Single Trace Query | <100ms | ~2.5ms | ✅ PASS |
| Aggregation Query | <1s | <50ms | ✅ PASS |
| Storage Efficiency | <10MB/1K | ~0.01MB/1K | ✅ PASS |

## Running Individual Tests

### Overhead Test
```bash
# Quick test
pytest tests/performance/test_overhead.py::test_complex_function_overhead -v

# Full suite
pytest tests/performance/test_overhead.py -v -s
```

### Query Speed Test
```bash
# Quick test
pytest tests/performance/test_query_speed.py::test_single_trace_query_speed -v

# Full suite (may take several minutes)
pytest tests/performance/test_query_speed.py -v -s
```

### Storage Efficiency Test
```bash
# Quick test
pytest tests/performance/test_storage_efficiency.py::test_storage_efficiency_simple -v

# Full suite
pytest tests/performance/test_storage_efficiency.py -v -s
```

## Understanding Results

### Good Results
- ✅ Tests pass with margin
- Performance well within targets
- No unexpected slowdowns

### Concerning Results
- ⚠️ Tests barely pass or fail
- Performance regression from previous runs
- High variance in measurements

### Action Items
If tests fail or show degraded performance:

1. **Check System Load:**
   - Close other applications
   - Run on dedicated machine if possible

2. **Verify Dependencies:**
   - DuckDB version
   - Python version (3.12+ required for PEP 669)

3. **Investigate Changes:**
   - Recent code changes
   - Database schema changes
   - Configuration changes

4. **Profile Bottlenecks:**
   - Use pytest-profiling
   - Check database query plans
   - Review instrumentation patterns

## Continuous Integration

### pytest.ini Configuration

```ini
[pytest]
markers =
    performance: marks tests as performance benchmarks (deselect with '-m "not performance"')
```

### CI/CD Recommendations

```yaml
# Fast CI (skip perf tests)
pytest -m "not performance" --tb=short

# Nightly performance runs
pytest -m performance -v --tb=short

# Performance regression detection
pytest -m performance --benchmark-compare
```

## Interpreting Overhead Results

### Why High Overhead is OK

PEP 669 with LINE events has high overhead for trivial functions. This is expected and not a concern because:

1. **Measurement Artifact:** Functions < 1µs are dominated by instrumentation
2. **Real Code is Different:** Real functions do actual work (I/O, computation)
3. **Selective Instrumentation:** Production uses include/exclude patterns

### Production Overhead Expectations

| Scenario | Overhead | Suitable For |
|----------|----------|--------------|
| Full tracing (dev/test) | 200-500% | Development, testing |
| Selective tracing | 50-200% | Production debugging |
| Minimal tracing (future) | <50% | Always-on production |

## Troubleshooting

### Tests Taking Too Long

**Problem:** Query speed tests take >5 minutes

**Solutions:**
- Reduce `TEST_EVENT_COUNT` in test_query_speed.py
- Run individual tests instead of full suite
- Use pytest-xdist for parallelization

### Inconsistent Results

**Problem:** Test results vary significantly between runs

**Solutions:**
- Increase iteration count for more stable averages
- Run on idle system (no other processes)
- Use fixed test data instead of random generation

### Python Version Issues

**Problem:** PEP 669 tests fail or skip

**Solutions:**
- Verify Python 3.12+ is installed
- Check pytest is using correct Python version
- Tests automatically skip on Python <3.12

## Future Enhancements

Planned improvements to the performance test suite:

1. **Benchmark Tracking:**
   - Store historical results
   - Detect performance regressions
   - Generate trend charts

2. **More Realistic Workloads:**
   - Real application traces
   - Load testing scenarios
   - Concurrency tests

3. **Profiling Integration:**
   - CPU profiling
   - Memory profiling
   - I/O profiling

4. **Cross-Platform Testing:**
   - Linux vs Windows vs macOS
   - Different Python versions
   - Different hardware configs

## References

- [PERFORMANCE_REPORT.md](./PERFORMANCE_REPORT.md) - Detailed validation report
- [PEP 669 Specification](https://peps.python.org/pep-0669/) - Low-impact monitoring
- [DuckDB Documentation](https://duckdb.org/docs/) - Database performance
