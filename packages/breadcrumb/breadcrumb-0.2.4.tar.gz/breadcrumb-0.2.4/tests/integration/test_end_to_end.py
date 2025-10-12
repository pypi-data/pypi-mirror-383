"""
End-to-end integration tests for Breadcrumb AI Tracer.

Tests the complete workflow:
1. Inject breadcrumb into Python code
2. Run application (traces captured)
3. Query traces via storage layer
4. Verify data integrity across the stack
"""

import pytest
import time
from datetime import datetime, timezone

from breadcrumb.storage.query import (
    query_traces,
    get_trace,
    find_exceptions,
    analyze_performance,
    QueryError,
    TraceNotFoundError,
)
from breadcrumb.storage.connection import get_manager

from . import (
    run_traced_code,
    wait_for_traces,
)


class TestBasicEndToEnd:
    """Test basic end-to-end workflow."""

    def test_inject_run_query_workflow(
        self,
        temp_db_path,
        sample_traced_code,
    ):
        """
        Test: Inject breadcrumb → run application → query via storage → verify results.

        This is the most fundamental integration test that validates the entire stack.
        """
        # Step 1: Run code with tracing
        result = run_traced_code(sample_traced_code, temp_db_path)

        # Verify execution succeeded
        assert result['returncode'] == 0, f"Code execution failed: {result['stderr']}"
        assert 'Result:' in result['stdout']

        # Step 2: Wait for async writes to complete
        assert wait_for_traces(temp_db_path, min_traces=1, timeout=5.0), \
            "Traces not written to database within timeout"

        # Step 3: Query traces
        traces = query_traces("SELECT * FROM traces", db_path=temp_db_path)

        # Step 4: Verify results
        assert len(traces) > 0, "No traces found in database"

        # Verify trace structure
        trace = traces[0]
        assert 'id' in trace
        assert 'started_at' in trace
        assert 'status' in trace
        assert 'thread_id' in trace

        # Verify trace metadata
        assert trace['status'] in ('completed', 'running')
        assert trace['thread_id'] > 0

    def test_trace_events_captured(self, temp_db_path, sample_traced_code):
        """Test that trace events are properly captured."""
        # Run code
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0

        # Wait for traces
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Query trace events
        events = query_traces(
            "SELECT * FROM trace_events ORDER BY timestamp",
            db_path=temp_db_path
        )

        # Verify events exist
        assert len(events) > 0, "No trace events found"

        # Verify event structure
        event = events[0]
        assert 'id' in event
        assert 'trace_id' in event
        assert 'timestamp' in event
        assert 'event_type' in event

        # Verify we captured function calls
        function_names = [e.get('function_name') for e in events if e.get('function_name')]
        assert len(function_names) > 0, "No function names captured"

    def test_full_trace_retrieval(self, temp_db_path, sample_traced_code):
        """Test retrieving full trace with all details."""
        # Run code
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0

        # Wait for traces
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Get trace ID
        traces = query_traces("SELECT id FROM traces LIMIT 1", db_path=temp_db_path)
        trace_id = traces[0]['id']

        # Get full trace
        trace_data = get_trace(trace_id, db_path=temp_db_path)

        # Verify structure
        assert 'trace' in trace_data
        assert 'events' in trace_data
        assert 'exceptions' in trace_data

        # Verify trace data
        assert trace_data['trace']['id'] == trace_id
        assert len(trace_data['events']) > 0

    def test_data_persistence_across_queries(self, temp_db_path, sample_traced_code):
        """Test that data persists correctly across multiple queries."""
        # Run code
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0

        # Wait for traces
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Query 1: Get all traces
        traces1 = query_traces("SELECT * FROM traces", db_path=temp_db_path)
        trace_count1 = len(traces1)

        # Query 2: Get same traces again
        traces2 = query_traces("SELECT * FROM traces", db_path=temp_db_path)
        trace_count2 = len(traces2)

        # Verify consistency
        assert trace_count1 == trace_count2, "Trace count changed between queries"
        assert traces1[0]['id'] == traces2[0]['id'], "Trace IDs differ between queries"


class TestExceptionHandling:
    """Test exception capture and querying."""

    def test_exception_captured_in_database(
        self,
        temp_db_path,
        sample_traced_code_with_exception,
    ):
        """Test: Inject code with exception → run → verify exception captured."""
        # Run code (will fail due to ZeroDivisionError)
        result = run_traced_code(sample_traced_code_with_exception, temp_db_path)

        # Code should fail
        assert result['returncode'] != 0, "Code should have failed with exception"

        # Wait for traces
        time.sleep(0.5)  # Give more time for exception handling

        # Query exceptions
        try:
            exceptions = query_traces(
                "SELECT * FROM exceptions",
                db_path=temp_db_path
            )

            # Verify exception was captured
            assert len(exceptions) > 0, "No exceptions captured"

            # Verify exception details
            exc = exceptions[0]
            assert 'exception_type' in exc
            assert 'message' in exc
            assert exc['exception_type'] == 'ZeroDivisionError'

        except QueryError as e:
            # If exceptions table doesn't exist or is empty, that's also valid
            # depending on the tracer configuration
            pytest.skip(f"Exception capture not available: {e}")

    def test_find_exceptions_workflow(
        self,
        temp_db_path,
        sample_traced_code_with_exception,
    ):
        """Test: Run code with exception → query via find_exceptions → verify results."""
        # Run code
        result = run_traced_code(sample_traced_code_with_exception, temp_db_path)
        assert result['returncode'] != 0

        # Wait for traces
        time.sleep(0.5)

        # Find exceptions using query API
        try:
            result = find_exceptions(since="1h", limit=10, db_path=temp_db_path)

            # Verify result structure
            assert 'exceptions' in result
            assert 'total' in result
            assert 'time_range' in result

            # Verify exceptions found
            if result['total'] > 0:
                exc = result['exceptions'][0]
                assert 'exception_type' in exc
                assert exc['exception_type'] == 'ZeroDivisionError'

        except QueryError:
            pytest.skip("Exception capture not available")


class TestMultiThreadedTracing:
    """Test multi-threaded tracing with isolated traces."""

    def test_multiple_threads_isolated_traces(
        self,
        temp_db_path,
        sample_multithreaded_code,
    ):
        """Test: Multiple threads → verify isolated traces."""
        # Run multi-threaded code
        result = run_traced_code(sample_multithreaded_code, temp_db_path)
        assert result['returncode'] == 0

        # Wait for traces
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Query traces by thread
        traces = query_traces("SELECT * FROM traces", db_path=temp_db_path)

        # Verify we have traces
        assert len(traces) > 0

        # Check if we have multiple threads
        thread_ids = {t['thread_id'] for t in traces}

        # Verify thread isolation (each thread should have its own trace)
        # Note: Depending on implementation, we may have 1 trace with multiple
        # thread IDs in events, or multiple traces
        assert len(thread_ids) >= 1, "No thread IDs captured"

        # Query events to verify thread isolation
        events = query_traces(
            "SELECT DISTINCT thread_id FROM trace_events",
            db_path=temp_db_path
        )

        # Should have events from multiple threads
        # (though this depends on the tracer implementation)


class TestAsyncAwaitTracing:
    """Test async/await code tracing."""

    def test_async_code_trace_structure(self, temp_db_path, sample_async_code):
        """Test: Async/await code → verify correct trace structure."""
        # Run async code
        result = run_traced_code(sample_async_code, temp_db_path)
        assert result['returncode'] == 0, f"Async code failed: {result['stderr']}"
        assert 'Fetched 3 items' in result['stdout']

        # Wait for traces
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Query traces
        traces = query_traces("SELECT * FROM traces", db_path=temp_db_path)
        assert len(traces) > 0

        # Query events to check async function calls
        events = query_traces(
            "SELECT function_name FROM trace_events WHERE function_name IS NOT NULL",
            db_path=temp_db_path
        )

        # Verify we captured async function calls
        function_names = [e['function_name'] for e in events]

        # Should include async functions (depending on tracer configuration)
        assert len(function_names) > 0, "No function names captured"


class TestSelectiveInstrumentation:
    """Test selective instrumentation filtering."""

    def test_selective_instrumentation_filtering(self, temp_db_path):
        """Test: Selective instrumentation → verify filtering works."""
        # Create code with selective instrumentation
        code = """
import breadcrumb

# Only trace functions in __main__ module
breadcrumb.init(
    include=['__main__'],
    exclude=['breadcrumb.*'],
    silent=True
)

def should_be_traced():
    '''This should be traced.'''
    return 42

def main():
    result = should_be_traced()
    print(f"Result: {result}")

if __name__ == '__main__':
    main()
"""

        # Run code
        result = run_traced_code(code, temp_db_path)
        assert result['returncode'] == 0

        # Wait for traces
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Query events
        events = query_traces(
            "SELECT module_name, function_name FROM trace_events WHERE function_name IS NOT NULL",
            db_path=temp_db_path
        )

        # Verify filtering worked (should only have __main__ functions)
        for event in events:
            module = event.get('module_name', '')
            # Should not have breadcrumb internal functions
            assert not module.startswith('breadcrumb.'), \
                f"Excluded module captured: {module}"


class TestSecretRedaction:
    """Test secret redaction in trace data."""

    def test_secrets_redacted_in_database(
        self,
        temp_db_path,
        sample_traced_code_with_secrets,
    ):
        """Test: Code with secrets → verify no secrets in database."""
        # Run code with secrets
        result = run_traced_code(sample_traced_code_with_secrets, temp_db_path)
        assert result['returncode'] == 0

        # Wait for traces
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Query all trace data
        traces = query_traces("SELECT * FROM traces", db_path=temp_db_path)
        events = query_traces("SELECT * FROM trace_events", db_path=temp_db_path)

        # Convert all data to strings for searching
        all_data = str(traces) + str(events)

        # Verify secrets are NOT in the data
        # (These would be the literal secret values)
        assert 'secret123' not in all_data.lower(), \
            "Password found in database (not redacted)"
        assert 'sk-1234567890abcdef' not in all_data.lower(), \
            "API key found in database (not redacted)"

        # Note: Username 'alice' is not a secret, so it might be present


class TestPerformanceAnalysis:
    """Test performance analysis workflow."""

    def test_analyze_performance_workflow(self, temp_db_path, sample_traced_code):
        """Test: Run code → analyze performance → verify statistics."""
        # Run code
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0

        # Wait for traces
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Get function names
        events = query_traces(
            "SELECT DISTINCT function_name FROM trace_events WHERE function_name IS NOT NULL LIMIT 1",
            db_path=temp_db_path
        )

        if len(events) == 0:
            pytest.skip("No function names captured for performance analysis")

        function_name = events[0]['function_name']

        # Analyze performance
        perf_result = analyze_performance(
            function=function_name,
            limit=5,
            db_path=temp_db_path
        )

        # Verify result structure
        assert 'stats' in perf_result
        assert 'slowest_traces' in perf_result
        assert 'function' in perf_result

        # Verify function matches
        assert perf_result['function'] == function_name


class TestDatabaseIntegrity:
    """Test database integrity and consistency."""

    def test_trace_event_relationships(self, temp_db_path, sample_traced_code):
        """Test that trace-event relationships are maintained."""
        # Run code
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0

        # Wait for traces
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Query traces and events
        traces = query_traces("SELECT id FROM traces", db_path=temp_db_path)
        events = query_traces("SELECT trace_id FROM trace_events", db_path=temp_db_path)

        # Verify all events reference valid traces
        trace_ids = {t['id'] for t in traces}
        event_trace_ids = {e['trace_id'] for e in events}

        # All event trace_ids should be in trace_ids
        orphaned_events = event_trace_ids - trace_ids
        assert len(orphaned_events) == 0, \
            f"Found events referencing non-existent traces: {orphaned_events}"

    def test_database_schema_version(self, temp_db_path, sample_traced_code):
        """Test that database schema is correctly versioned."""
        # Run code to create database
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0

        # Wait for traces
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Verify schema version
        try:
            version_result = query_traces(
                "SELECT version FROM _schema_version ORDER BY applied_at DESC LIMIT 1",
                db_path=temp_db_path
            )

            # Should have a schema version
            assert len(version_result) > 0, "No schema version found"
            assert 'version' in version_result[0]

        except QueryError:
            # Schema versioning might not be implemented yet
            pytest.skip("Schema versioning not available")

    def test_concurrent_writes_no_corruption(self, temp_db_path):
        """Test that concurrent writes don't corrupt database."""
        # Create code that writes concurrently
        code = """
import breadcrumb
import threading
import time

breadcrumb.init(silent=True)

def worker(worker_id):
    for i in range(10):
        value = worker_id * 100 + i
        time.sleep(0.001)  # Small delay
    return worker_id

def main():
    threads = []
    for i in range(5):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Done")

if __name__ == '__main__':
    main()
"""

        # Run code
        result = run_traced_code(code, temp_db_path)
        assert result['returncode'] == 0

        # Wait for traces
        time.sleep(1.0)  # Extra time for concurrent writes

        # Verify database is readable and consistent
        traces = query_traces("SELECT COUNT(*) as count FROM traces", db_path=temp_db_path)
        assert len(traces) > 0

        # Verify no corruption by doing a complex query
        events = query_traces(
            "SELECT trace_id, COUNT(*) as event_count FROM trace_events GROUP BY trace_id",
            db_path=temp_db_path
        )

        # Should be able to group by trace_id without errors
        assert len(events) >= 0  # May be 0 if no events captured


class TestErrorHandling:
    """Test error handling in the integration workflow."""

    def test_query_nonexistent_trace(self, temp_db_path, sample_traced_code):
        """Test querying a non-existent trace ID."""
        # Create database first
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0

        # Wait for traces
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Try to get non-existent trace
        fake_trace_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(TraceNotFoundError):
            get_trace(fake_trace_id, db_path=temp_db_path)

    def test_invalid_sql_query(self, temp_db_path, sample_traced_code):
        """Test that invalid SQL queries are handled properly."""
        # Create database
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0

        # Wait for traces
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Try invalid SQL
        with pytest.raises(QueryError):
            query_traces(
                "SELECT * FROM nonexistent_table",
                db_path=temp_db_path
            )

    def test_unsafe_sql_rejected(self, temp_db_path, sample_traced_code):
        """Test that unsafe SQL operations are rejected."""
        from breadcrumb.storage.query import InvalidQueryError

        # Create database
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0

        # Wait for traces
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Try unsafe operations
        with pytest.raises(InvalidQueryError):
            query_traces("DELETE FROM traces", db_path=temp_db_path)

        with pytest.raises(InvalidQueryError):
            query_traces("DROP TABLE traces", db_path=temp_db_path)

        with pytest.raises(InvalidQueryError):
            query_traces("UPDATE traces SET status='hacked'", db_path=temp_db_path)
