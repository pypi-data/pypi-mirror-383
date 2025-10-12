# -*- coding: utf-8 -*-
"""
Phase 2: Storage Layer Demo

Demonstrates the DuckDB storage layer with async writing and querying.
Note: Phase 1 (instrumentation) and Phase 2 (storage) are not yet integrated.

This example shows the storage layer working with manually created trace data.

Usage:
    python -X utf8 examples/phase2_storage_demo.py
"""

import sys
sys.path.insert(0, 'src')

import uuid
import time
from datetime import datetime, timedelta, timezone

from breadcrumb.storage.async_writer import TraceWriter
from breadcrumb.storage.query import get_trace, query_traces, find_exceptions


def main():
    print("=" * 70)
    print("PHASE 2: STORAGE LAYER DEMO")
    print("=" * 70)
    print()

    # Step 1: Initialize storage
    print("[1] Initializing DuckDB storage...")
    writer = TraceWriter(batch_size=5)
    writer.start()
    print(f"    Database: {writer.db_path}")
    print(f"    Batch size: {writer.batch_size}")
    print(f"    Status: STARTED")
    print()

    # Step 2: Write sample traces
    print("[2] Writing sample traces...")
    trace_ids = []

    # Create successful trace
    trace_id_1 = str(uuid.uuid4())
    trace_ids.append(trace_id_1)

    writer.write_trace(
        trace_id=trace_id_1,
        started_at=datetime.now(timezone.utc),
        ended_at=datetime.now(timezone.utc) + timedelta(milliseconds=45),
        status='completed',
        thread_id=12345
    )

    # Write some events for trace 1
    event_id_1 = str(uuid.uuid4())
    writer.write_trace_event(
        event_id=event_id_1,
        trace_id=trace_id_1,
        timestamp=datetime.now(timezone.utc),
        event_type='call',
        function_name='fetch_data',
        module_name='myapp.api',
        data={'args': {'url': 'https://api.example.com'}}
    )

    event_id_2 = str(uuid.uuid4())
    writer.write_trace_event(
        event_id=event_id_2,
        trace_id=trace_id_1,
        timestamp=datetime.now(timezone.utc) + timedelta(milliseconds=40),
        event_type='return',
        function_name='fetch_data',
        module_name='myapp.api',
        data={'return_value': {'status': 200}}
    )

    print(f"    [✓] Trace {trace_id_1[:8]}... (completed)")

    # Create failed trace with exception
    trace_id_2 = str(uuid.uuid4())
    trace_ids.append(trace_id_2)

    writer.write_trace(
        trace_id=trace_id_2,
        started_at=datetime.now(timezone.utc),
        ended_at=datetime.now(timezone.utc) + timedelta(milliseconds=12),
        status='failed',
        thread_id=12346
    )

    event_id_3 = str(uuid.uuid4())
    writer.write_trace_event(
        event_id=event_id_3,
        trace_id=trace_id_2,
        timestamp=datetime.now(timezone.utc),
        event_type='call',
        function_name='process_payment',
        module_name='myapp.billing',
    )

    exception_id_1 = str(uuid.uuid4())
    writer.write_exception(
        exception_id=exception_id_1,
        event_id=event_id_3,
        trace_id=trace_id_2,
        exception_type='PaymentError',
        message='Insufficient funds',
        stack_trace='Traceback (most recent call last):\\n  File "billing.py", line 42\\n    raise PaymentError(...)'
    )

    print(f"    [✓] Trace {trace_id_2[:8]}... (failed with exception)")

    # Create running trace
    trace_id_3 = str(uuid.uuid4())
    trace_ids.append(trace_id_3)

    writer.write_trace(
        trace_id=trace_id_3,
        started_at=datetime.now(timezone.utc),
        status='running',
        thread_id=12347
    )

    print(f"    [✓] Trace {trace_id_3[:8]}... (still running)")
    print()

    # Step 3: Flush to database
    print("[3] Flushing to database...")
    time.sleep(0.3)  # Wait for async writer to flush
    writer.stop()
    print("    [✓] All data persisted")
    print()

    # Step 4: Query traces
    print("[4] Querying traces...")
    print()

    # Get specific trace
    print("    [Query 1] Get trace by ID:")
    trace_data = get_trace(trace_id_1, db_path=writer.db_path)
    trace = trace_data['trace']
    events = trace_data['events']
    print(f"      Trace ID:   {trace['id'][:8]}...")
    print(f"      Status:     {trace['status']}")
    print(f"      Started:    {trace['started_at']}")
    print(f"      Ended:      {trace['ended_at']}")
    print(f"      Events:     {len(events)}")
    print()

    # Query all traces
    print("    [Query 2] Get all traces:")
    all_traces = query_traces(
        "SELECT * FROM traces ORDER BY started_at DESC",
        db_path=writer.db_path
    )
    print(f"      Total traces: {len(all_traces)}")
    for t in all_traces:
        print(f"        - {t['id'][:8]}... | {t['status']:10s} | {t['thread_id']}")
    print()

    # Find exceptions
    print("    [Query 3] Find exceptions:")
    exc_result = find_exceptions(since="1h", limit=10, db_path=writer.db_path)
    print(f"      Total exceptions: {exc_result['total']}")
    for exc in exc_result['exceptions']:
        print(f"        - {exc['exception_type']}: {exc['message']}")
    print()

    # Query by status
    print("    [Query 4] Get failed traces:")
    failed_traces = query_traces(
        "SELECT * FROM traces WHERE status = ?",
        params=['failed'],
        db_path=writer.db_path
    )
    print(f"      Failed traces: {len(failed_traces)}")
    print()

    # Step 5: Demonstrate features
    print("[5] Storage Features:")
    print("    " + "-" * 66)
    print("    [x] Async batch writing (100ms or 100 events)")
    print("    [x] DuckDB embedded database")
    print("    [x] Thread-safe connection pooling")
    print("    [x] Automatic schema initialization")
    print("    [x] SQL injection prevention")
    print("    [x] Query timeout protection (30s)")
    print("    [x] Retention policy (automatic cleanup)")
    print("    [x] Schema migration system")
    print("    " + "-" * 66)
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"  SUCCESS: Stored and queried {len(all_traces)} traces")
    print(f"  Database: {writer.db_path}")
    print()
    print("  What's Working:")
    print("    [x] Trace/event/exception storage")
    print("    [x] Async batch writing with backpressure")
    print("    [x] Safe query interface")
    print("    [x] Retention policy")
    print("    [x] Schema migrations")
    print()
    print("  What's Not Yet Integrated:")
    print("    [ ] Integration with instrumentation (Phase 1 is separate)")
    print("    [ ] MCP Server (Phase 3 - not started)")
    print("    [ ] CLI Interface (Phase 4 - not started)")
    print()
    print("  Next Steps:")
    print("    - Phase 6: Connect instrumentation backends to storage")
    print("    - Phase 3-4: Build MCP Server and CLI")
    print()
    print("=" * 70)


if __name__ == '__main__':
    main()
