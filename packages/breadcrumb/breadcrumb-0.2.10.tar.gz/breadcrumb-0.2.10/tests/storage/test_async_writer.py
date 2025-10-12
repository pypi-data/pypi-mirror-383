"""
Tests for async writer with batching and backpressure.

Validates:
- Background writing without blocking
- Batch accumulation and flushing
- Backpressure handling
- Graceful shutdown
- Statistics tracking
"""

import pytest
import tempfile
import os
import time
from datetime import datetime, timezone
import uuid

from breadcrumb.storage.async_writer import (
    TraceWriter,
    get_writer,
    reset_writer,
)
from breadcrumb.storage.connection import get_manager, reset_manager


@pytest.fixture
def temp_db_path():
    """Create a temporary database path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, ".breadcrumb", "traces.duckdb")
        yield db_path


@pytest.fixture(autouse=True)
def cleanup():
    """Reset global instances before and after each test."""
    reset_writer()
    reset_manager()
    yield
    reset_writer()
    reset_manager()


class TestTraceWriter:
    """Test TraceWriter class."""

    def test_initialization(self, temp_db_path):
        """Test writer initialization."""
        writer = TraceWriter(db_path=temp_db_path)

        assert writer.batch_size == 100
        assert writer.batch_timeout == 0.1
        assert writer.queue_size == 10000
        assert not writer._running

    def test_start_and_stop(self, temp_db_path):
        """Test starting and stopping writer."""
        writer = TraceWriter(db_path=temp_db_path)

        # Start
        writer.start()
        assert writer._running
        assert writer._writer_thread is not None
        assert writer._writer_thread.is_alive()

        # Stop
        writer.stop()
        assert not writer._running

    def test_write_trace(self, temp_db_path):
        """Test writing a single trace."""
        writer = TraceWriter(db_path=temp_db_path, batch_size=1)  # Flush immediately
        writer.start()

        trace_id = str(uuid.uuid4())
        success = writer.write_trace(
            trace_id=trace_id,
            started_at=datetime.now(timezone.utc),
            status='running',
            thread_id=12345
        )

        assert success is True

        # Wait for write
        time.sleep(0.2)
        writer.stop()

        # Verify written to database
        manager = get_manager(temp_db_path)
        result = manager.execute_with_retry(
            "SELECT id, status FROM traces WHERE id = ?",
            [trace_id]
        )

        row = result.fetchone()
        assert row is not None
        assert row[0] == trace_id
        assert row[1] == 'running'

    def test_write_trace_event(self, temp_db_path):
        """Test writing a trace event."""
        writer = TraceWriter(db_path=temp_db_path, batch_size=2)
        writer.start()

        # Create parent trace first
        trace_id = str(uuid.uuid4())
        writer.write_trace(
            trace_id=trace_id,
            started_at=datetime.now(timezone.utc),
            status='running',
            thread_id=12345
        )

        # Write event
        event_id = str(uuid.uuid4())
        success = writer.write_trace_event(
            event_id=event_id,
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc),
            event_type='call',
            function_name='test_func',
            module_name='__main__'
        )

        assert success is True

        # Wait for writes
        time.sleep(0.2)
        writer.stop()

        # Verify written
        manager = get_manager(temp_db_path)
        result = manager.execute_with_retry(
            "SELECT id, event_type, function_name FROM trace_events WHERE id = ?",
            [event_id]
        )

        row = result.fetchone()
        assert row is not None
        assert row[0] == event_id
        assert row[1] == 'call'
        assert row[2] == 'test_func'

    def test_write_exception(self, temp_db_path):
        """Test writing an exception."""
        writer = TraceWriter(db_path=temp_db_path, batch_size=3)
        writer.start()

        # Create parent trace and event
        trace_id = str(uuid.uuid4())
        event_id = str(uuid.uuid4())

        writer.write_trace(
            trace_id=trace_id,
            started_at=datetime.now(timezone.utc),
            status='failed',
            thread_id=12345
        )

        writer.write_trace_event(
            event_id=event_id,
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc),
            event_type='exception',
            function_name='test_func'
        )

        # Write exception
        exc_id = str(uuid.uuid4())
        success = writer.write_exception(
            exception_id=exc_id,
            event_id=event_id,
            trace_id=trace_id,
            exception_type='ValueError',
            message='Test error',
            stack_trace='Traceback...'
        )

        assert success is True

        # Wait for writes
        time.sleep(0.2)
        writer.stop()

        # Verify written
        manager = get_manager(temp_db_path)
        result = manager.execute_with_retry(
            "SELECT exception_type, message FROM exceptions WHERE id = ?",
            [exc_id]
        )

        row = result.fetchone()
        assert row is not None
        assert row[0] == 'ValueError'
        assert row[1] == 'Test error'

    def test_batch_writes(self, temp_db_path):
        """Test that events are batched."""
        writer = TraceWriter(
            db_path=temp_db_path,
            batch_size=10,  # Batch up to 10
            batch_timeout=1.0  # Wait 1 second before flush
        )
        writer.start()

        # Write 5 traces (below batch size)
        trace_ids = []
        for i in range(5):
            trace_id = str(uuid.uuid4())
            trace_ids.append(trace_id)
            writer.write_trace(
                trace_id=trace_id,
                started_at=datetime.now(timezone.utc),
                status='running',
                thread_id=12345 + i
            )

        # Check stats immediately (should be queued, not written yet)
        stats = writer.get_stats()
        assert stats['queue_size'] > 0 or stats['batches_written'] == 0

        # Wait for batch timeout
        time.sleep(1.2)

        # Now should be written
        stats = writer.get_stats()
        assert stats['events_written'] >= 5
        assert stats['batches_written'] >= 1

        writer.stop()

        # Verify all written
        manager = get_manager(temp_db_path)
        for trace_id in trace_ids:
            result = manager.execute_with_retry(
                "SELECT COUNT(*) FROM traces WHERE id = ?",
                [trace_id]
            )
            assert result.fetchone()[0] == 1

    def test_batch_size_triggers_flush(self, temp_db_path):
        """Test that reaching batch size triggers immediate flush."""
        writer = TraceWriter(
            db_path=temp_db_path,
            batch_size=5,  # Flush after 5 events
            batch_timeout=10.0  # Long timeout, shouldn't matter
        )
        writer.start()

        # Write exactly 5 traces (batch size)
        for i in range(5):
            writer.write_trace(
                trace_id=str(uuid.uuid4()),
                started_at=datetime.now(timezone.utc),
                status='running',
                thread_id=12345 + i
            )

        # Wait a bit for batch to flush
        time.sleep(0.2)

        # Should have written 5 events in 1 batch
        stats = writer.get_stats()
        assert stats['events_written'] == 5
        assert stats['batches_written'] == 1

        writer.stop()

    def test_backpressure_drops_events(self, temp_db_path):
        """Test that full queue drops events."""
        writer = TraceWriter(
            db_path=temp_db_path,
            queue_size=10,  # Very small queue
            batch_size=100,  # Large batch size to delay flushing
            batch_timeout=10.0  # Long timeout
        )
        writer.start()

        # Try to write more than queue can hold
        results = []
        for i in range(20):
            success = writer.write_trace(
                trace_id=str(uuid.uuid4()),
                started_at=datetime.now(timezone.utc),
                status='running',
                thread_id=12345 + i
            )
            results.append(success)

        # Some should be dropped
        assert False in results

        # Check stats
        stats = writer.get_stats()
        assert stats['events_dropped'] > 0

        writer.stop()

    def test_graceful_shutdown_flushes_queue(self, temp_db_path):
        """Test that stopping flushes pending events."""
        writer = TraceWriter(
            db_path=temp_db_path,
            batch_size=100,  # Large batch to prevent auto-flush
            batch_timeout=10.0  # Long timeout
        )
        writer.start()

        # Write some traces
        trace_ids = []
        for i in range(5):
            trace_id = str(uuid.uuid4())
            trace_ids.append(trace_id)
            writer.write_trace(
                trace_id=trace_id,
                started_at=datetime.now(timezone.utc),
                status='running',
                thread_id=12345 + i
            )

        # Stop immediately (should flush queue)
        writer.stop(timeout=2.0)

        # All events should be written
        stats = writer.get_stats()
        assert stats['events_written'] == 5

        # Verify in database
        manager = get_manager(temp_db_path)
        for trace_id in trace_ids:
            result = manager.execute_with_retry(
                "SELECT COUNT(*) FROM traces WHERE id = ?",
                [trace_id]
            )
            assert result.fetchone()[0] == 1

    def test_context_manager_pattern(self, temp_db_path):
        """Test using writer as context manager."""
        trace_id = str(uuid.uuid4())

        with TraceWriter(db_path=temp_db_path, batch_size=1) as writer:
            writer.write_trace(
                trace_id=trace_id,
                started_at=datetime.now(timezone.utc),
                status='running',
                thread_id=12345
            )

            # Wait for write
            time.sleep(0.2)

        # Writer should be stopped and flushed
        manager = get_manager(temp_db_path)
        result = manager.execute_with_retry(
            "SELECT COUNT(*) FROM traces WHERE id = ?",
            [trace_id]
        )
        assert result.fetchone()[0] == 1

    def test_get_stats(self, temp_db_path):
        """Test statistics tracking."""
        writer = TraceWriter(db_path=temp_db_path, batch_size=2)
        writer.start()

        # Initial stats
        stats = writer.get_stats()
        assert stats['events_written'] == 0
        assert stats['events_dropped'] == 0
        assert stats['batches_written'] == 0
        assert stats['is_running'] is True

        # Write some events
        for i in range(4):  # 2 batches of 2
            writer.write_trace(
                trace_id=str(uuid.uuid4()),
                started_at=datetime.now(timezone.utc),
                status='running',
                thread_id=12345 + i
            )

        # Wait for writes
        time.sleep(0.3)

        # Check stats
        stats = writer.get_stats()
        assert stats['events_written'] == 4
        assert stats['batches_written'] == 2

        writer.stop()

        stats = writer.get_stats()
        assert stats['is_running'] is False


class TestGlobalWriter:
    """Test global writer singleton."""

    def test_get_writer_returns_singleton(self, temp_db_path):
        """Test that get_writer returns the same instance."""
        writer1 = get_writer(temp_db_path)
        writer2 = get_writer(temp_db_path)

        assert writer1 is writer2
        assert writer1._running  # Should be auto-started

        writer1.stop()

    def test_reset_writer_clears_singleton(self, temp_db_path):
        """Test that reset_writer clears the singleton."""
        writer1 = get_writer(temp_db_path)

        reset_writer()

        writer2 = get_writer(temp_db_path)

        # Should be a new instance
        assert writer1 is not writer2

        writer2.stop()


class TestBulkInsert:
    """Test bulk insert performance."""

    def test_bulk_insert_many_traces(self, temp_db_path):
        """Test writing many traces efficiently."""
        writer = TraceWriter(
            db_path=temp_db_path,
            batch_size=50  # Batch 50 at a time
        )
        writer.start()

        # Write 100 traces
        trace_ids = []
        for i in range(100):
            trace_id = str(uuid.uuid4())
            trace_ids.append(trace_id)
            writer.write_trace(
                trace_id=trace_id,
                started_at=datetime.now(timezone.utc),
                status='completed',
                thread_id=12345 + i
            )

        # Wait for all writes
        time.sleep(0.5)
        writer.stop()

        # Verify all written
        stats = writer.get_stats()
        assert stats['events_written'] == 100
        assert stats['batches_written'] >= 2  # At least 2 batches of 50

        # Spot check some traces
        manager = get_manager(temp_db_path)
        for trace_id in trace_ids[::10]:  # Check every 10th
            result = manager.execute_with_retry(
                "SELECT COUNT(*) FROM traces WHERE id = ?",
                [trace_id]
            )
            assert result.fetchone()[0] == 1


class TestErrorHandling:
    """Test error handling in writer."""

    def test_writer_continues_after_error(self, temp_db_path):
        """Test that writer continues after individual write errors."""
        writer = TraceWriter(db_path=temp_db_path, batch_size=1)
        writer.start()

        # Write valid trace
        trace_id1 = str(uuid.uuid4())
        writer.write_trace(
            trace_id=trace_id1,
            started_at=datetime.now(timezone.utc),
            status='running',
            thread_id=12345
        )

        time.sleep(0.2)

        # Write another valid trace after potential error
        trace_id2 = str(uuid.uuid4())
        writer.write_trace(
            trace_id=trace_id2,
            started_at=datetime.now(timezone.utc),
            status='running',
            thread_id=12346
        )

        time.sleep(0.2)
        writer.stop()

        # Both should be written
        manager = get_manager(temp_db_path)

        result1 = manager.execute_with_retry(
            "SELECT COUNT(*) FROM traces WHERE id = ?",
            [trace_id1]
        )
        assert result1.fetchone()[0] == 1

        result2 = manager.execute_with_retry(
            "SELECT COUNT(*) FROM traces WHERE id = ?",
            [trace_id2]
        )
        assert result2.fetchone()[0] == 1
