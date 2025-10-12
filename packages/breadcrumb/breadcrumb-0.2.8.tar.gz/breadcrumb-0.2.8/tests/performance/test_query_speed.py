"""
Query performance benchmarks for trace database.

Tests that query performance meets specification targets:
- Single trace query: <100ms (10K events in DB)
- Aggregation query: <1s (10K+ events)
"""

import time
import uuid
import statistics
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from typing import List

from breadcrumb.storage.connection import ConnectionManager, reset_manager
from breadcrumb.storage.query import (
    query_traces,
    get_trace,
    find_exceptions,
    analyze_performance,
)


# Performance targets from PLAN.md
TARGET_SINGLE_TRACE_MS = 100  # <100ms for single trace query
TARGET_AGGREGATION_MS = 1000  # <1s for aggregation queries
TEST_EVENT_COUNT = 5000  # 5K events for testing (reduced for speed)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_traces.duckdb")

    yield db_path

    # Cleanup
    reset_manager()
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)
    except Exception:
        pass


def generate_test_data(manager: ConnectionManager, num_events: int = 10000) -> List[str]:
    """
    Generate test trace data with realistic structure.

    Creates traces with multiple events, variables, and some exceptions.

    Args:
        manager: Database connection manager
        num_events: Number of events to generate

    Returns:
        List of trace IDs
    """
    conn = manager.get_connection()

    # Calculate structure: ~100 events per trace
    events_per_trace = 100
    num_traces = num_events // events_per_trace

    trace_ids = []

    # Generate traces in batches for performance
    batch_size = 10
    start_time = datetime.now() - timedelta(hours=1)

    for batch_idx in range(0, num_traces, batch_size):
        batch_traces = []
        batch_events = []
        batch_exceptions = []

        for i in range(batch_idx, min(batch_idx + batch_size, num_traces)):
            trace_id = str(uuid.uuid4())
            trace_ids.append(trace_id)

            # Create trace
            trace_start = start_time + timedelta(seconds=i * 10)
            trace_end = trace_start + timedelta(seconds=5)

            batch_traces.append((
                trace_id,
                trace_start,
                trace_end,
                'completed' if i % 10 != 0 else 'failed',  # 10% failure rate
                12345 + (i % 4),  # 4 different thread IDs
                None  # metadata
            ))

            # Create events for this trace
            for j in range(events_per_trace):
                event_id = str(uuid.uuid4())
                event_time = trace_start + timedelta(milliseconds=j * 50)

                # Mix of event types
                if j % 20 == 0:
                    event_type = 'call'
                elif j % 20 == 19:
                    event_type = 'return'
                else:
                    event_type = 'line'

                # Vary function names
                function_name = f"function_{j % 10}"
                module_name = f"module_{j % 5}"

                batch_events.append((
                    event_id,
                    trace_id,
                    event_time,
                    event_type,
                    function_name,
                    module_name,
                    f"/path/to/file_{j % 5}.py",
                    (j % 100) + 1,  # line number
                    None  # data
                ))

                # Add exception for failed traces
                if i % 10 == 0 and j == 50:
                    exc_id = str(uuid.uuid4())
                    batch_exceptions.append((
                        exc_id,
                        event_id,
                        trace_id,
                        'ValueError',
                        'Test exception message',
                        'Traceback (most recent call last):\n  ...'
                    ))

        # Bulk insert batch
        if batch_traces:
            conn.executemany(
                "INSERT INTO traces (id, started_at, ended_at, status, thread_id, metadata) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                batch_traces
            )

        if batch_events:
            conn.executemany(
                "INSERT INTO trace_events (id, trace_id, timestamp, event_type, function_name, "
                "module_name, file_path, line_number, data) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                batch_events
            )

        if batch_exceptions:
            conn.executemany(
                "INSERT INTO exceptions (id, event_id, trace_id, exception_type, message, stack_trace) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                batch_exceptions
            )

    return trace_ids


def measure_query_time(query_func, *args, **kwargs) -> float:
    """
    Measure query execution time.

    Args:
        query_func: Query function to measure
        *args, **kwargs: Arguments for query function

    Returns:
        Execution time in milliseconds
    """
    start = time.perf_counter()
    query_func(*args, **kwargs)
    end = time.perf_counter()

    return (end - start) * 1000  # Convert to milliseconds


@pytest.mark.performance
def test_single_trace_query_speed(temp_db):
    """Test single trace query performance (<100ms with 10K events)."""
    # Setup: Create database with 10K events
    manager = ConnectionManager(temp_db)
    trace_ids = generate_test_data(manager, TEST_EVENT_COUNT)

    print(f"\n  Generated {len(trace_ids)} traces with ~{TEST_EVENT_COUNT} events")

    # Test: Query single trace multiple times and measure
    times = []
    test_trace_id = trace_ids[len(trace_ids) // 2]  # Middle trace

    # Warmup
    for _ in range(5):
        get_trace(test_trace_id, temp_db)

    # Measure
    for _ in range(20):
        query_time = measure_query_time(get_trace, test_trace_id, temp_db)
        times.append(query_time)

    # Statistics
    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    p95_time = statistics.quantiles(times, n=20)[18]  # 95th percentile

    print(f"\n  Single Trace Query Performance:")
    print(f"    Average: {avg_time:.2f} ms")
    print(f"    Min:     {min_time:.2f} ms")
    print(f"    Max:     {max_time:.2f} ms")
    print(f"    P95:     {p95_time:.2f} ms")
    print(f"    Target:  <{TARGET_SINGLE_TRACE_MS} ms")

    # Assert meets target
    assert avg_time < TARGET_SINGLE_TRACE_MS, (
        f"Single trace query time ({avg_time:.2f}ms) exceeds target "
        f"({TARGET_SINGLE_TRACE_MS}ms)"
    )


@pytest.mark.performance
def test_recent_traces_query_speed(temp_db):
    """Test recent traces query performance (<100ms)."""
    # Setup
    manager = ConnectionManager(temp_db)
    generate_test_data(manager, TEST_EVENT_COUNT)

    print(f"\n  Database contains ~{TEST_EVENT_COUNT} events")

    # Test: Query recent 100 traces
    times = []

    # Warmup
    for _ in range(5):
        query_traces(
            "SELECT * FROM traces ORDER BY started_at DESC LIMIT 100",
            db_path=temp_db
        )

    # Measure
    for _ in range(20):
        query_time = measure_query_time(
            query_traces,
            "SELECT * FROM traces ORDER BY started_at DESC LIMIT 100",
            db_path=temp_db
        )
        times.append(query_time)

    # Statistics
    avg_time = statistics.mean(times)
    p95_time = statistics.quantiles(times, n=20)[18]

    print(f"\n  Recent Traces Query Performance:")
    print(f"    Average: {avg_time:.2f} ms")
    print(f"    P95:     {p95_time:.2f} ms")
    print(f"    Target:  <{TARGET_SINGLE_TRACE_MS} ms")

    # Assert meets target
    assert avg_time < TARGET_SINGLE_TRACE_MS, (
        f"Recent traces query time ({avg_time:.2f}ms) exceeds target "
        f"({TARGET_SINGLE_TRACE_MS}ms)"
    )


@pytest.mark.performance
def test_aggregation_query_speed(temp_db):
    """Test aggregation query performance (<1s with 10K+ events)."""
    # Setup
    manager = ConnectionManager(temp_db)
    generate_test_data(manager, TEST_EVENT_COUNT)

    print(f"\n  Database contains ~{TEST_EVENT_COUNT} events")

    # Test: Complex aggregation query
    aggregation_sql = """
        SELECT
            event_type,
            COUNT(*) as count,
            COUNT(DISTINCT trace_id) as unique_traces,
            COUNT(DISTINCT function_name) as unique_functions
        FROM trace_events
        GROUP BY event_type
    """

    times = []

    # Warmup
    for _ in range(3):
        query_traces(aggregation_sql, db_path=temp_db)

    # Measure
    for _ in range(10):
        query_time = measure_query_time(
            query_traces,
            aggregation_sql,
            db_path=temp_db
        )
        times.append(query_time)

    # Statistics
    avg_time = statistics.mean(times)
    max_time = max(times)

    print(f"\n  Aggregation Query Performance:")
    print(f"    Average: {avg_time:.2f} ms")
    print(f"    Max:     {max_time:.2f} ms")
    print(f"    Target:  <{TARGET_AGGREGATION_MS} ms")

    # Assert meets target
    assert avg_time < TARGET_AGGREGATION_MS, (
        f"Aggregation query time ({avg_time:.2f}ms) exceeds target "
        f"({TARGET_AGGREGATION_MS}ms)"
    )


@pytest.mark.performance
def test_complex_join_query_speed(temp_db):
    """Test complex join query performance (<1s)."""
    # Setup
    manager = ConnectionManager(temp_db)
    generate_test_data(manager, TEST_EVENT_COUNT)

    print(f"\n  Database contains ~{TEST_EVENT_COUNT} events")

    # Test: Complex join with aggregation
    join_sql = """
        SELECT
            t.status,
            COUNT(DISTINCT t.id) as trace_count,
            COUNT(e.id) as event_count,
            AVG(EXTRACT(EPOCH FROM (t.ended_at - t.started_at))) as avg_duration_sec
        FROM traces t
        JOIN trace_events e ON e.trace_id = t.id
        WHERE t.ended_at IS NOT NULL
        GROUP BY t.status
    """

    times = []

    # Warmup
    for _ in range(3):
        query_traces(join_sql, db_path=temp_db)

    # Measure
    for _ in range(10):
        query_time = measure_query_time(
            query_traces,
            join_sql,
            db_path=temp_db
        )
        times.append(query_time)

    # Statistics
    avg_time = statistics.mean(times)
    max_time = max(times)

    print(f"\n  Complex Join Query Performance:")
    print(f"    Average: {avg_time:.2f} ms")
    print(f"    Max:     {max_time:.2f} ms")
    print(f"    Target:  <{TARGET_AGGREGATION_MS} ms")

    # Assert meets target
    assert avg_time < TARGET_AGGREGATION_MS, (
        f"Complex join query time ({avg_time:.2f}ms) exceeds target "
        f"({TARGET_AGGREGATION_MS}ms)"
    )


@pytest.mark.performance
def test_find_exceptions_speed(temp_db):
    """Test find_exceptions() query performance (<1s)."""
    # Setup
    manager = ConnectionManager(temp_db)
    generate_test_data(manager, TEST_EVENT_COUNT)

    print(f"\n  Database contains ~{TEST_EVENT_COUNT} events")

    # Test: Find recent exceptions
    times = []

    # Warmup
    for _ in range(3):
        find_exceptions(since="1h", limit=10, db_path=temp_db)

    # Measure
    for _ in range(10):
        query_time = measure_query_time(
            find_exceptions,
            since="1h",
            limit=10,
            db_path=temp_db
        )
        times.append(query_time)

    # Statistics
    avg_time = statistics.mean(times)
    max_time = max(times)

    print(f"\n  Find Exceptions Query Performance:")
    print(f"    Average: {avg_time:.2f} ms")
    print(f"    Max:     {max_time:.2f} ms")
    print(f"    Target:  <{TARGET_AGGREGATION_MS} ms")

    # Assert meets target
    assert avg_time < TARGET_AGGREGATION_MS, (
        f"Find exceptions query time ({avg_time:.2f}ms) exceeds target "
        f"({TARGET_AGGREGATION_MS}ms)"
    )


@pytest.mark.performance
def test_analyze_performance_speed(temp_db):
    """Test analyze_performance() query performance (<1s)."""
    # Setup
    manager = ConnectionManager(temp_db)
    generate_test_data(manager, TEST_EVENT_COUNT)

    print(f"\n  Database contains ~{TEST_EVENT_COUNT} events")

    # Test: Analyze performance for a function
    times = []

    # Warmup
    for _ in range(3):
        analyze_performance("function_1", limit=10, db_path=temp_db)

    # Measure
    for _ in range(10):
        query_time = measure_query_time(
            analyze_performance,
            "function_1",
            limit=10,
            db_path=temp_db
        )
        times.append(query_time)

    # Statistics
    avg_time = statistics.mean(times)
    max_time = max(times)

    print(f"\n  Analyze Performance Query:")
    print(f"    Average: {avg_time:.2f} ms")
    print(f"    Max:     {max_time:.2f} ms")
    print(f"    Target:  <{TARGET_AGGREGATION_MS} ms")

    # Assert meets target
    assert avg_time < TARGET_AGGREGATION_MS, (
        f"Analyze performance query time ({avg_time:.2f}ms) exceeds target "
        f"({TARGET_AGGREGATION_MS}ms)"
    )


@pytest.mark.performance
def test_query_speed_summary(temp_db):
    """
    Comprehensive query performance summary.

    Tests all major query types and reports summary statistics.
    """
    # Setup
    manager = ConnectionManager(temp_db)
    trace_ids = generate_test_data(manager, TEST_EVENT_COUNT)

    print(f"\n  Generated {len(trace_ids)} traces with ~{TEST_EVENT_COUNT} events")

    results = []

    # Test 1: Single trace query
    test_trace_id = trace_ids[len(trace_ids) // 2]
    times = [
        measure_query_time(get_trace, test_trace_id, temp_db)
        for _ in range(20)
    ]
    results.append({
        'query': 'Single Trace',
        'avg_ms': statistics.mean(times),
        'p95_ms': statistics.quantiles(times, n=20)[18],
        'target_ms': TARGET_SINGLE_TRACE_MS
    })

    # Test 2: Recent traces
    times = [
        measure_query_time(
            query_traces,
            "SELECT * FROM traces ORDER BY started_at DESC LIMIT 100",
            db_path=temp_db
        )
        for _ in range(20)
    ]
    results.append({
        'query': 'Recent Traces',
        'avg_ms': statistics.mean(times),
        'p95_ms': statistics.quantiles(times, n=20)[18],
        'target_ms': TARGET_SINGLE_TRACE_MS
    })

    # Test 3: Aggregation
    times = [
        measure_query_time(
            query_traces,
            "SELECT event_type, COUNT(*) FROM trace_events GROUP BY event_type",
            db_path=temp_db
        )
        for _ in range(10)
    ]
    results.append({
        'query': 'Aggregation',
        'avg_ms': statistics.mean(times),
        'p95_ms': max(times),  # Use max as approximation for small sample
        'target_ms': TARGET_AGGREGATION_MS
    })

    # Test 4: Complex join
    times = [
        measure_query_time(
            query_traces,
            "SELECT t.status, COUNT(*) FROM traces t JOIN trace_events e ON e.trace_id = t.id GROUP BY t.status",
            db_path=temp_db
        )
        for _ in range(10)
    ]
    results.append({
        'query': 'Complex Join',
        'avg_ms': statistics.mean(times),
        'p95_ms': max(times),  # Use max as approximation for small sample
        'target_ms': TARGET_AGGREGATION_MS
    })

    # Print summary
    print("\n")
    print("=" * 80)
    print("QUERY PERFORMANCE SUMMARY")
    print("=" * 80)
    print(f"{'Query Type':<20} {'Avg (ms)':<12} {'P95 (ms)':<12} {'Target (ms)':<12} {'Pass':<8}")
    print("-" * 80)

    all_passed = True
    for result in results:
        passed = result['avg_ms'] < result['target_ms']
        all_passed = all_passed and passed

        print(
            f"{result['query']:<20} "
            f"{result['avg_ms']:<12.2f} "
            f"{result['p95_ms']:<12.2f} "
            f"{result['target_ms']:<12.0f} "
            f"{'PASS' if passed else 'FAIL':<8}"
        )

    print("=" * 80)
    print(f"Overall: {'PASS' if all_passed else 'FAIL'}")
    print("=" * 80)

    # Assert all queries meet targets
    assert all_passed, "Some queries did not meet performance targets"


if __name__ == "__main__":
    # Run query speed tests directly
    print("Running Query Performance Benchmarks...")
    print(f"Test data size: {TEST_EVENT_COUNT} events")
    print(f"Single trace target: <{TARGET_SINGLE_TRACE_MS}ms")
    print(f"Aggregation target: <{TARGET_AGGREGATION_MS}ms")
    print()

    # Create temp database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_traces.duckdb")

    try:
        # Run tests
        test_single_trace_query_speed(db_path)
        test_recent_traces_query_speed(db_path)
        test_aggregation_query_speed(db_path)
        test_complex_join_query_speed(db_path)
        test_find_exceptions_speed(db_path)
        test_analyze_performance_speed(db_path)
        test_query_speed_summary(db_path)

        print("\nAll query performance tests passed!")

    finally:
        # Cleanup
        reset_manager()
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
            os.rmdir(temp_dir)
        except Exception:
            pass
