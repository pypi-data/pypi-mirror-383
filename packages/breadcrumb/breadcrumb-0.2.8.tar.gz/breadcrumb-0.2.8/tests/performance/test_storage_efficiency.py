"""
Storage efficiency benchmarks for trace database.

Tests that storage efficiency meets specification targets:
- Storage size: <10MB per 1000 function calls
"""

import os
import uuid
import pytest
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any

from breadcrumb.storage.connection import ConnectionManager, reset_manager
from breadcrumb.storage.async_writer import TraceWriter, reset_writer


# Performance targets from PLAN.md
TARGET_BYTES_PER_CALL = 10 * 1024  # 10KB per function call
TARGET_MB_PER_1K_CALLS = 10  # <10MB per 1000 calls
TEST_FUNCTION_CALLS = 1000  # 1000 function calls for testing


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_traces.duckdb")

    yield db_path

    # Cleanup
    reset_writer()
    reset_manager()
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)
    except Exception:
        pass


def get_database_size(db_path: str) -> int:
    """
    Get database file size in bytes.

    Args:
        db_path: Path to database file

    Returns:
        File size in bytes
    """
    if not os.path.exists(db_path):
        return 0

    return os.path.getsize(db_path)


def generate_function_calls_simple(
    writer: TraceWriter,
    num_calls: int
) -> Dict[str, Any]:
    """
    Generate simple function calls with minimal data.

    This represents the best-case scenario for storage efficiency.

    Args:
        writer: Trace writer instance
        num_calls: Number of function calls to generate

    Returns:
        Dict with generation metadata
    """
    trace_id = str(uuid.uuid4())
    start_time = datetime.now()

    # Write trace
    writer.write_trace(
        trace_id=trace_id,
        started_at=start_time,
        status='running',
        thread_id=12345,
    )

    # Write function call events
    for i in range(num_calls):
        event_time = start_time + timedelta(milliseconds=i)

        # Call event
        call_event_id = str(uuid.uuid4())
        writer.write_trace_event(
            event_id=call_event_id,
            trace_id=trace_id,
            timestamp=event_time,
            event_type='call',
            function_name='simple_function',
            module_name='test_module',
            file_path='/path/to/file.py',
            line_number=10,
            data={'args': {'a': 1, 'b': 2}}
        )

        # Return event
        return_event_id = str(uuid.uuid4())
        writer.write_trace_event(
            event_id=return_event_id,
            trace_id=trace_id,
            timestamp=event_time + timedelta(microseconds=100),
            event_type='return',
            function_name='simple_function',
            module_name='test_module',
            file_path='/path/to/file.py',
            line_number=12,
            data={'return_value': 3}
        )

    # End trace
    writer.write_trace(
        trace_id=trace_id,
        started_at=start_time,
        ended_at=start_time + timedelta(milliseconds=num_calls),
        status='completed',
        thread_id=12345,
    )

    return {
        'trace_id': trace_id,
        'num_calls': num_calls,
        'num_events': num_calls * 2,  # call + return
    }


def generate_function_calls_complex(
    writer: TraceWriter,
    num_calls: int
) -> Dict[str, Any]:
    """
    Generate complex function calls with realistic data.

    This represents a typical scenario with arguments, return values,
    and occasional exceptions.

    Args:
        writer: Trace writer instance
        num_calls: Number of function calls to generate

    Returns:
        Dict with generation metadata
    """
    trace_id = str(uuid.uuid4())
    start_time = datetime.now()

    # Write trace
    writer.write_trace(
        trace_id=trace_id,
        started_at=start_time,
        status='running',
        thread_id=12345,
        metadata={'purpose': 'performance_test', 'version': '1.0'}
    )

    num_exceptions = 0

    # Write function call events with complex data
    for i in range(num_calls):
        event_time = start_time + timedelta(milliseconds=i * 10)

        # Call event with complex arguments
        call_event_id = str(uuid.uuid4())
        writer.write_trace_event(
            event_id=call_event_id,
            trace_id=trace_id,
            timestamp=event_time,
            event_type='call',
            function_name=f'function_{i % 10}',
            module_name='test_module',
            file_path=f'/path/to/file_{i % 5}.py',
            line_number=10 + (i % 100),
            data={
                'args': {
                    'param1': i,
                    'param2': f'string_value_{i}',
                    'param3': [1, 2, 3, 4, 5],
                    'param4': {'key': 'value', 'nested': {'a': 1, 'b': 2}}
                },
                'kwargs': {
                    'timeout': 30,
                    'retry': True
                }
            }
        )

        # Add exception for 10% of calls
        if i % 10 == 0:
            exc_event_id = str(uuid.uuid4())
            writer.write_trace_event(
                event_id=exc_event_id,
                trace_id=trace_id,
                timestamp=event_time + timedelta(microseconds=50),
                event_type='exception',
                function_name=f'function_{i % 10}',
                module_name='test_module',
                file_path=f'/path/to/file_{i % 5}.py',
                line_number=15 + (i % 100),
                data={}
            )

            exc_id = str(uuid.uuid4())
            writer.write_exception(
                exception_id=exc_id,
                event_id=exc_event_id,
                trace_id=trace_id,
                exception_type='ValueError',
                message=f'Test exception {i}',
                stack_trace='Traceback (most recent call last):\n  File "test.py", line 42, in test\n    raise ValueError("test")\nValueError: test'
            )
            num_exceptions += 1

        # Return event
        return_event_id = str(uuid.uuid4())
        writer.write_trace_event(
            event_id=return_event_id,
            trace_id=trace_id,
            timestamp=event_time + timedelta(microseconds=100),
            event_type='return',
            function_name=f'function_{i % 10}',
            module_name='test_module',
            file_path=f'/path/to/file_{i % 5}.py',
            line_number=20 + (i % 100),
            data={
                'return_value': {
                    'status': 'success' if i % 10 != 0 else 'error',
                    'result': i * 2,
                    'metadata': {'elapsed_ms': i * 0.5}
                }
            }
        )

    # End trace
    writer.write_trace(
        trace_id=trace_id,
        started_at=start_time,
        ended_at=start_time + timedelta(milliseconds=num_calls * 10),
        status='failed' if num_exceptions > 0 else 'completed',
        thread_id=12345,
        metadata={'purpose': 'performance_test', 'version': '1.0'}
    )

    return {
        'trace_id': trace_id,
        'num_calls': num_calls,
        'num_events': num_calls * 2 + num_exceptions,
        'num_exceptions': num_exceptions,
    }


@pytest.mark.performance
def test_storage_efficiency_simple(temp_db):
    """Test storage efficiency with simple function calls."""
    # Get initial database size
    initial_size = get_database_size(temp_db)

    # Generate data
    writer = TraceWriter(db_path=temp_db)
    writer.start()

    try:
        metadata = generate_function_calls_simple(writer, TEST_FUNCTION_CALLS)

        # Stop writer to flush all events
        writer.stop(timeout=10.0)

        # Get final database size
        final_size = get_database_size(temp_db)
        data_size = final_size - initial_size

        # Calculate metrics
        bytes_per_call = data_size / TEST_FUNCTION_CALLS
        mb_total = data_size / (1024 * 1024)
        mb_per_1k_calls = (bytes_per_call * 1000) / (1024 * 1024)

        print(f"\n  Simple Function Calls Storage Efficiency:")
        print(f"    Function calls: {TEST_FUNCTION_CALLS}")
        print(f"    Total events:   {metadata['num_events']}")
        print(f"    Database size:  {data_size:,} bytes ({mb_total:.2f} MB)")
        print(f"    Bytes/call:     {bytes_per_call:.2f} bytes")
        print(f"    MB per 1K:      {mb_per_1k_calls:.2f} MB")
        print(f"    Target:         <{TARGET_MB_PER_1K_CALLS} MB per 1K calls")

        # Assert meets target
        assert mb_per_1k_calls < TARGET_MB_PER_1K_CALLS, (
            f"Storage efficiency ({mb_per_1k_calls:.2f} MB per 1K calls) exceeds target "
            f"({TARGET_MB_PER_1K_CALLS} MB per 1K calls)"
        )

        assert bytes_per_call < TARGET_BYTES_PER_CALL, (
            f"Storage efficiency ({bytes_per_call:.2f} bytes/call) exceeds target "
            f"({TARGET_BYTES_PER_CALL} bytes/call)"
        )

    finally:
        writer.stop()


@pytest.mark.performance
def test_storage_efficiency_complex(temp_db):
    """Test storage efficiency with complex function calls."""
    # Get initial database size
    initial_size = get_database_size(temp_db)

    # Generate data
    writer = TraceWriter(db_path=temp_db)
    writer.start()

    try:
        metadata = generate_function_calls_complex(writer, TEST_FUNCTION_CALLS)

        # Stop writer to flush all events
        writer.stop(timeout=10.0)

        # Get final database size
        final_size = get_database_size(temp_db)
        data_size = final_size - initial_size

        # Calculate metrics
        bytes_per_call = data_size / TEST_FUNCTION_CALLS
        mb_total = data_size / (1024 * 1024)
        mb_per_1k_calls = (bytes_per_call * 1000) / (1024 * 1024)

        print(f"\n  Complex Function Calls Storage Efficiency:")
        print(f"    Function calls: {TEST_FUNCTION_CALLS}")
        print(f"    Total events:   {metadata['num_events']}")
        print(f"    Exceptions:     {metadata['num_exceptions']}")
        print(f"    Database size:  {data_size:,} bytes ({mb_total:.2f} MB)")
        print(f"    Bytes/call:     {bytes_per_call:.2f} bytes")
        print(f"    MB per 1K:      {mb_per_1k_calls:.2f} MB")
        print(f"    Target:         <{TARGET_MB_PER_1K_CALLS} MB per 1K calls")

        # Assert meets target
        assert mb_per_1k_calls < TARGET_MB_PER_1K_CALLS, (
            f"Storage efficiency ({mb_per_1k_calls:.2f} MB per 1K calls) exceeds target "
            f"({TARGET_MB_PER_1K_CALLS} MB per 1K calls)"
        )

        # Allow slightly more for complex calls (up to 15KB per call)
        assert bytes_per_call < TARGET_BYTES_PER_CALL * 1.5, (
            f"Storage efficiency ({bytes_per_call:.2f} bytes/call) significantly exceeds target "
            f"({TARGET_BYTES_PER_CALL * 1.5:.2f} bytes/call for complex data)"
        )

    finally:
        writer.stop()


@pytest.mark.performance
def test_storage_efficiency_scaling(temp_db):
    """Test storage efficiency scaling with increasing data."""
    writer = TraceWriter(db_path=temp_db)
    writer.start()

    try:
        results = []

        # Test with different data sizes
        test_sizes = [100, 500, 1000]

        for size in test_sizes:
            # Get size before
            size_before = get_database_size(temp_db)

            # Generate data
            metadata = generate_function_calls_simple(writer, size)

            # Flush
            writer.stop(timeout=10.0)
            writer.start()

            # Get size after
            size_after = get_database_size(temp_db)
            delta_size = size_after - size_before

            # Calculate metrics
            bytes_per_call = delta_size / size
            mb_per_1k = (bytes_per_call * 1000) / (1024 * 1024)

            results.append({
                'calls': size,
                'size_bytes': delta_size,
                'bytes_per_call': bytes_per_call,
                'mb_per_1k': mb_per_1k
            })

        # Print summary
        print("\n  Storage Efficiency Scaling:")
        print(f"    {'Calls':<10} {'Size (bytes)':<15} {'Bytes/call':<15} {'MB per 1K':<15}")
        print("    " + "-" * 60)

        for result in results:
            print(
                f"    {result['calls']:<10} "
                f"{result['size_bytes']:<15,} "
                f"{result['bytes_per_call']:<15.2f} "
                f"{result['mb_per_1k']:<15.2f}"
            )

        # Assert all sizes meet target
        for result in results:
            assert result['mb_per_1k'] < TARGET_MB_PER_1K_CALLS, (
                f"Storage efficiency at {result['calls']} calls "
                f"({result['mb_per_1k']:.2f} MB per 1K) exceeds target "
                f"({TARGET_MB_PER_1K_CALLS} MB per 1K)"
            )

    finally:
        writer.stop()


@pytest.mark.performance
def test_storage_compression_ratio(temp_db):
    """Test DuckDB compression effectiveness."""
    # DuckDB uses compression by default, so we measure the compression ratio

    writer = TraceWriter(db_path=temp_db)
    writer.start()

    try:
        # Generate highly compressible data (repeated strings)
        trace_id = str(uuid.uuid4())
        start_time = datetime.now()

        writer.write_trace(
            trace_id=trace_id,
            started_at=start_time,
            status='running',
            thread_id=12345,
        )

        # Write 1000 identical events (should compress well)
        for i in range(1000):
            event_id = str(uuid.uuid4())
            writer.write_trace_event(
                event_id=event_id,
                trace_id=trace_id,
                timestamp=start_time + timedelta(milliseconds=i),
                event_type='call',
                function_name='repeated_function',
                module_name='repeated_module',
                file_path='/path/to/same/file.py',
                line_number=42,
                data={'args': {'same': 'value', 'every': 'time'}}
            )

        writer.stop(timeout=10.0)

        # Get database size
        db_size = get_database_size(temp_db)
        bytes_per_event = db_size / 1000

        print(f"\n  Storage Compression:")
        print(f"    Events:         1000 (identical)")
        print(f"    Database size:  {db_size:,} bytes ({db_size / 1024:.2f} KB)")
        print(f"    Bytes/event:    {bytes_per_event:.2f} bytes")

        # With compression, identical events should be very efficient
        # Expect <5KB per event for highly compressible data
        assert bytes_per_event < 5000, (
            f"Compression appears ineffective: {bytes_per_event:.2f} bytes/event"
        )

    finally:
        writer.stop()


@pytest.mark.performance
def test_storage_efficiency_summary(temp_db):
    """
    Comprehensive storage efficiency summary.

    Tests multiple scenarios and reports summary statistics.
    """
    writer = TraceWriter(db_path=temp_db)
    writer.start()

    try:
        results = []

        # Test 1: Simple calls
        size_before = get_database_size(temp_db)
        generate_function_calls_simple(writer, TEST_FUNCTION_CALLS)
        writer.stop(timeout=10.0)
        writer.start()
        size_after = get_database_size(temp_db)
        delta = size_after - size_before

        results.append({
            'scenario': 'Simple Calls',
            'calls': TEST_FUNCTION_CALLS,
            'size_mb': delta / (1024 * 1024),
            'mb_per_1k': (delta / TEST_FUNCTION_CALLS * 1000) / (1024 * 1024)
        })

        # Test 2: Complex calls
        size_before = get_database_size(temp_db)
        generate_function_calls_complex(writer, TEST_FUNCTION_CALLS)
        writer.stop(timeout=10.0)
        size_after = get_database_size(temp_db)
        delta = size_after - size_before

        results.append({
            'scenario': 'Complex Calls',
            'calls': TEST_FUNCTION_CALLS,
            'size_mb': delta / (1024 * 1024),
            'mb_per_1k': (delta / TEST_FUNCTION_CALLS * 1000) / (1024 * 1024)
        })

        # Print summary
        print("\n")
        print("=" * 80)
        print("STORAGE EFFICIENCY SUMMARY")
        print("=" * 80)
        print(f"{'Scenario':<20} {'Calls':<10} {'Size (MB)':<12} {'MB per 1K':<12} {'Pass':<8}")
        print("-" * 80)

        all_passed = True
        for result in results:
            passed = result['mb_per_1k'] < TARGET_MB_PER_1K_CALLS
            all_passed = all_passed and passed

            print(
                f"{result['scenario']:<20} "
                f"{result['calls']:<10} "
                f"{result['size_mb']:<12.2f} "
                f"{result['mb_per_1k']:<12.2f} "
                f"{'PASS' if passed else 'FAIL':<8}"
            )

        print("-" * 80)
        print(f"Target: <{TARGET_MB_PER_1K_CALLS} MB per 1K calls")
        print("=" * 80)
        print(f"Overall: {'PASS' if all_passed else 'FAIL'}")
        print("=" * 80)

        # Assert all scenarios meet target
        assert all_passed, "Some scenarios did not meet storage efficiency targets"

    finally:
        writer.stop()


if __name__ == "__main__":
    # Run storage efficiency tests directly
    print("Running Storage Efficiency Benchmarks...")
    print(f"Test data size: {TEST_FUNCTION_CALLS} function calls")
    print(f"Target: <{TARGET_MB_PER_1K_CALLS}MB per 1K calls")
    print()

    # Create temp database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_traces.duckdb")

    try:
        # Run tests
        test_storage_efficiency_simple(db_path)
        test_storage_efficiency_complex(db_path)
        test_storage_efficiency_scaling(db_path)
        test_storage_compression_ratio(db_path)
        test_storage_efficiency_summary(db_path)

        print("\nAll storage efficiency tests passed!")

    finally:
        # Cleanup
        reset_writer()
        reset_manager()
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
            os.rmdir(temp_dir)
        except Exception:
            pass
