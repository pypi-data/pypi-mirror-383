"""
Async writer for non-blocking trace persistence.

Provides queue-based background writing with batching and backpressure handling.
"""

import threading
import queue
import time
import atexit
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from collections import Counter

from breadcrumb.storage.connection import get_manager
from breadcrumb.storage.value_truncation import truncate_dict, MAX_VALUE_SIZE
import json


# Batch configuration
DEFAULT_BATCH_SIZE = 100  # Max events per batch
DEFAULT_BATCH_TIMEOUT = 0.1  # 100ms - flush if no new events
DEFAULT_QUEUE_SIZE = 10000  # Max queue size before backpressure

# Shutdown timeout
SHUTDOWN_TIMEOUT = 5.0  # seconds


class TraceWriter:
    """
    Asynchronous trace event writer with batching and backpressure.

    Features:
    - Queue-based: instrumentation pushes events to queue, background thread writes
    - Batch writes: accumulates events for 100ms or 100 events, then bulk insert
    - Backpressure: if queue full, drops events with warning
    - Shutdown hook: flushes queue on process exit
    - Thread-safe: all operations are thread-safe

    Example:
        writer = TraceWriter()
        writer.start()

        # Write trace event
        writer.write_trace('trace-123', timestamp, 'running', 12345)

        # Shutdown gracefully
        writer.stop()
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
        batch_timeout: float = DEFAULT_BATCH_TIMEOUT,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        max_queue_breaks: int = 3,
        backend_ref: Optional[Any] = None,
        max_value_size: int = MAX_VALUE_SIZE,
    ):
        """
        Initialize async writer.

        Args:
            db_path: Optional database path
            batch_size: Maximum events per batch before flush
            batch_timeout: Maximum time to wait before flush (seconds)
            queue_size: Maximum queue size before backpressure
            max_queue_breaks: Maximum queue overflow warnings before auto-stop (default: 3)
            backend_ref: Reference to backend for diagnostics (optional)
        """
        self.db_path = db_path
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.queue_size = queue_size
        self.max_queue_breaks = max_queue_breaks
        self.backend_ref = backend_ref
        self._max_value_size = max_value_size

        # Event queue
        self._queue: queue.Queue = queue.Queue(maxsize=queue_size)

        # Background writer thread
        self._writer_thread: Optional[threading.Thread] = None
        self._running = False
        self._stop_event = threading.Event()

        # Statistics
        self._events_written = 0
        self._events_dropped = 0
        self._batches_written = 0
        self._queue_breaks = 0  # Number of times queue was full
        self._lock = threading.Lock()

        # Track recent events for diagnostics
        self._recent_dropped_functions: Counter = Counter()

        # Register shutdown hook
        atexit.register(self.stop)

    def start(self) -> None:
        """Start background writer thread."""
        if self._running:
            return

        self._running = True
        self._stop_event.clear()

        self._writer_thread = threading.Thread(
            target=self._writer_loop,
            daemon=False,  # NOT daemon - we need to wait for flush on exit!
            name="breadcrumb-writer"
        )
        self._writer_thread.start()

    def stop(self, timeout: float = SHUTDOWN_TIMEOUT) -> None:
        """
        Stop background writer and flush pending events.

        Args:
            timeout: Maximum time to wait for flush (seconds)
        """
        if not self._running:
            return

        # Signal stop
        self._stop_event.set()
        self._running = False

        # Wait for thread to finish
        if self._writer_thread and self._writer_thread.is_alive():
            self._writer_thread.join(timeout=timeout)

    def write_trace(
        self,
        trace_id: str,
        started_at: datetime,
        status: str,
        thread_id: int,
        metadata: Optional[Dict[str, Any]] = None,
        ended_at: Optional[datetime] = None,
    ) -> bool:
        """
        Write trace record (async).

        Args:
            trace_id: Trace UUID
            started_at: Trace start timestamp
            status: Trace status ('running', 'completed', 'failed')
            thread_id: Thread ID
            metadata: Optional metadata dict
            ended_at: Optional end timestamp

        Returns:
            True if queued successfully, False if dropped due to backpressure
        """
        event = {
            'type': 'trace',
            'trace_id': trace_id,
            'started_at': started_at,
            'ended_at': ended_at,
            'status': status,
            'thread_id': thread_id,
            'metadata': metadata,
        }

        return self._enqueue(event)

    def update_trace(
        self,
        trace_id: str,
        ended_at: Optional[datetime] = None,
        status: Optional[str] = None,
    ) -> bool:
        """
        Update trace record (async).

        Args:
            trace_id: Trace UUID to update
            ended_at: Optional end timestamp
            status: Optional status update ('running', 'completed', 'failed')

        Returns:
            True if queued successfully, False if dropped due to backpressure
        """
        event = {
            'type': 'trace_update',
            'trace_id': trace_id,
            'ended_at': ended_at,
            'status': status,
        }

        return self._enqueue(event)

    def write_trace_event(
        self,
        event_id: str,
        trace_id: str,
        timestamp: datetime,
        event_type: str,
        function_name: Optional[str] = None,
        module_name: Optional[str] = None,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Write trace event record (async).

        Args:
            event_id: Event UUID
            trace_id: Parent trace UUID
            timestamp: Event timestamp
            event_type: Event type ('call', 'return', 'line', 'exception')
            function_name: Function name
            module_name: Module name
            file_path: Source file path
            line_number: Source line number
            data: Event data dict

        Returns:
            True if queued successfully, False if dropped
        """
        event = {
            'type': 'trace_event',
            'event_id': event_id,
            'trace_id': trace_id,
            'timestamp': timestamp,
            'event_type': event_type,
            'function_name': function_name,
            'module_name': module_name,
            'file_path': file_path,
            'line_number': line_number,
            'data': data,
        }

        return self._enqueue(event)

    def write_exception(
        self,
        exception_id: str,
        event_id: str,
        trace_id: str,
        exception_type: str,
        message: str,
        stack_trace: Optional[str] = None,
    ) -> bool:
        """
        Write exception record (async).

        Args:
            exception_id: Exception UUID
            event_id: Parent event UUID
            trace_id: Parent trace UUID
            exception_type: Exception class name
            message: Exception message
            stack_trace: Stack trace string

        Returns:
            True if queued successfully, False if dropped
        """
        event = {
            'type': 'exception',
            'exception_id': exception_id,
            'event_id': event_id,
            'trace_id': trace_id,
            'exception_type': exception_type,
            'message': message,
            'stack_trace': stack_trace,
        }

        return self._enqueue(event)

    def _enqueue(self, event: Dict[str, Any]) -> bool:
        """
        Enqueue event for async writing.

        Args:
            event: Event dict

        Returns:
            True if queued, False if dropped
        """
        try:
            self._queue.put_nowait(event)
            return True
        except queue.Full:
            # Track dropped function for diagnostics
            if event['type'] == 'trace_event':
                module = event.get('module_name', 'unknown')
                func = event.get('function_name', 'unknown')
                self._recent_dropped_functions[(module, func)] += 1

            # Backpressure: queue is full, drop event
            with self._lock:
                self._events_dropped += 1
                dropped_count = self._events_dropped

            # Log warning with diagnostics every 100 events
            if dropped_count % 100 == 1:
                self._handle_queue_break(dropped_count)

            return False

    def _handle_queue_break(self, dropped_count: int) -> None:
        """
        Handle queue overflow - show diagnostics and auto-stop if needed.

        Args:
            dropped_count: Total number of dropped events
        """
        import sys

        with self._lock:
            self._queue_breaks += 1
            current_breaks = self._queue_breaks

        # Show warning with diagnostics
        print(
            f"\nWARNING: Breadcrumb event queue full. "
            f"Dropped {dropped_count} events total.",
            file=sys.stderr
        )

        # Show most frequent dropped functions
        if self._recent_dropped_functions:
            print("\nMost frequent calls being dropped:", file=sys.stderr)
            for (module, func), count in self._recent_dropped_functions.most_common(10):
                print(f"  {module}.{func}: {count} calls", file=sys.stderr)

        # Check if we should auto-stop
        if current_breaks >= self.max_queue_breaks:
            print(
                f"\n🛑 QUEUE OVERFLOW LIMIT REACHED ({self.max_queue_breaks} breaks)",
                file=sys.stderr
            )
            self._generate_final_report()
            self._emergency_stop()

    def _generate_final_report(self) -> None:
        """Generate final diagnostic report before stopping."""
        import sys

        print("\n" + "=" * 60, file=sys.stderr)
        print("BREADCRUMB AUTO-STOP REPORT", file=sys.stderr)
        print("=" * 60, file=sys.stderr)

        # Writer statistics
        stats = self.get_stats()
        print(f"\nWriter Statistics:", file=sys.stderr)
        print(f"  Events written: {stats['events_written']}", file=sys.stderr)
        print(f"  Events dropped: {stats['events_dropped']}", file=sys.stderr)
        print(f"  Queue breaks: {self._queue_breaks}", file=sys.stderr)
        print(f"  Batches written: {stats['batches_written']}", file=sys.stderr)

        # Most dropped functions
        if self._recent_dropped_functions:
            print(f"\nTop 20 Functions Causing Overflow:", file=sys.stderr)
            for (module, func), count in self._recent_dropped_functions.most_common(20):
                print(f"  {module}.{func}: {count} dropped events", file=sys.stderr)

        # Auto-filter statistics (if backend available)
        if self.backend_ref is not None:
            try:
                truncation_summary = self.backend_ref.get_truncation_summary()
                if truncation_summary.get('auto_filter_enabled'):
                    print(f"\nSmart Auto-Filter Statistics:", file=sys.stderr)
                    print(f"  Truncated functions: {truncation_summary['truncated_functions']}", file=sys.stderr)
                    print(f"  Auto-filtered events: {truncation_summary['total_dropped_events']}", file=sys.stderr)

                    if truncation_summary.get('details'):
                        print(f"\nTop 10 Auto-Filtered Functions:", file=sys.stderr)
                        for detail in truncation_summary['details'][:10]:
                            print(
                                f"  {detail['module']}.{detail['function']}: "
                                f"{detail['dropped_count']} auto-filtered",
                                file=sys.stderr
                            )
            except Exception:
                pass  # Backend not available or error

        print("\nRecommendations:", file=sys.stderr)
        print("  1. Use --exclude patterns to filter noisy frameworks", file=sys.stderr)
        print("  2. Increase --sample-rate (e.g., 0.1 for 10% sampling)", file=sys.stderr)
        print("  3. Focus tracing on specific modules with --include", file=sys.stderr)
        print("  4. Smart auto-filter is already active (threshold: 100 calls/10s)", file=sys.stderr)
        print("=" * 60 + "\n", file=sys.stderr)

    def _emergency_stop(self) -> None:
        """Emergency stop - signal all tracing to halt."""
        import sys
        print("Stopping breadcrumb tracing...", file=sys.stderr)

        # Signal backend to stop if available
        if self.backend_ref is not None:
            try:
                self.backend_ref.stop()
            except Exception:
                pass

        # Stop writer
        self.stop()

    def _writer_loop(self) -> None:
        """Background writer thread loop."""
        manager = get_manager(self.db_path)
        batch: List[Dict[str, Any]] = []
        last_flush = time.time()

        while self._running or not self._queue.empty():
            try:
                # Try to get event with timeout
                timeout = max(0.001, self.batch_timeout - (time.time() - last_flush))
                event = self._queue.get(timeout=timeout)
                batch.append(event)

                # Flush if batch is full
                if len(batch) >= self.batch_size:
                    self._flush_batch(manager, batch)
                    batch = []
                    last_flush = time.time()

            except queue.Empty:
                # Timeout: flush if batch timeout exceeded
                if batch and (time.time() - last_flush) >= self.batch_timeout:
                    self._flush_batch(manager, batch)
                    batch = []
                    last_flush = time.time()

                # Check if we should stop
                if self._stop_event.is_set():
                    break

        # Flush remaining events on shutdown
        if batch:
            self._flush_batch(manager, batch)

    def _flush_batch(self, manager, batch: List[Dict[str, Any]]) -> None:
        """
        Flush batch of events to database.

        Args:
            manager: Connection manager
            batch: List of events to write
        """
        if not batch:
            return

        try:
            # Group events by type for efficient bulk insert
            traces = [e for e in batch if e['type'] == 'trace']
            trace_updates = [e for e in batch if e['type'] == 'trace_update']
            trace_events = [e for e in batch if e['type'] == 'trace_event']
            exceptions = [e for e in batch if e['type'] == 'exception']

            with manager.get_connection_context() as conn:
                # Bulk insert traces
                if traces:
                    self._insert_traces(conn, traces)

                # Bulk update traces
                if trace_updates:
                    self._update_traces(conn, trace_updates)

                # Bulk insert trace events
                if trace_events:
                    self._insert_trace_events(conn, trace_events)

                # Bulk insert exceptions
                if exceptions:
                    self._insert_exceptions(conn, exceptions)

                # CRITICAL: Explicit commit to ensure data is persisted!
                conn.commit()

            # Update statistics
            with self._lock:
                self._events_written += len(batch)
                self._batches_written += 1

        except Exception as e:
            import sys
            print(f"ERROR: Failed to write batch: {e}", file=sys.stderr)

    def _insert_traces(self, conn, traces: List[Dict[str, Any]]) -> None:
        """Bulk insert traces."""
        # Use executemany for efficiency
        conn.executemany("""
            INSERT INTO traces (id, started_at, ended_at, status, thread_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            (
                t['trace_id'],
                t['started_at'],
                t.get('ended_at'),
                t['status'],
                t['thread_id'],
                json.dumps(truncate_dict(t.get('metadata', {}), self._max_value_size)) if t.get('metadata') else None
            )
            for t in traces
        ])

    def _update_traces(self, conn, trace_updates: List[Dict[str, Any]]) -> None:
        """Bulk update traces."""
        for update in trace_updates:
            # Build UPDATE query dynamically based on provided fields
            updates = []
            params = []

            if update.get('ended_at') is not None:
                updates.append("ended_at = ?")
                params.append(update['ended_at'])

            if update.get('status') is not None:
                updates.append("status = ?")
                params.append(update['status'])

            if not updates:
                continue  # Nothing to update

            # Add trace_id to params
            params.append(update['trace_id'])

            # Execute update
            query = f"UPDATE traces SET {', '.join(updates)} WHERE id = ?"
            conn.execute(query, params)

    def _insert_trace_events(self, conn, events: List[Dict[str, Any]]) -> None:
        """Bulk insert trace events."""
        conn.executemany("""
            INSERT INTO trace_events (id, trace_id, timestamp, event_type, function_name, module_name, file_path, line_number, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (
                e['event_id'],
                e['trace_id'],
                e['timestamp'],
                e['event_type'],
                e.get('function_name'),
                e.get('module_name'),
                e.get('file_path'),
                e.get('line_number'),
                json.dumps(truncate_dict(e.get('data', {}), self._max_value_size)) if e.get('data') else None
            )
            for e in events
        ])

    def _insert_exceptions(self, conn, exceptions: List[Dict[str, Any]]) -> None:
        """Bulk insert exceptions."""
        conn.executemany("""
            INSERT INTO exceptions (id, event_id, trace_id, exception_type, message, stack_trace)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            (
                e['exception_id'],
                e['event_id'],
                e['trace_id'],
                e['exception_type'],
                e['message'],
                e.get('stack_trace')
            )
            for e in exceptions
        ])

    def get_stats(self) -> Dict[str, int]:
        """
        Get writer statistics.

        Returns:
            Dict with events_written, events_dropped, batches_written, queue_size
        """
        with self._lock:
            return {
                'events_written': self._events_written,
                'events_dropped': self._events_dropped,
                'batches_written': self._batches_written,
                'queue_size': self._queue.qsize(),
                'is_running': self._running,
            }

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False


# Global writer instance
_global_writer: Optional[TraceWriter] = None
_global_writer_lock = threading.Lock()


def get_writer(db_path: Optional[str] = None) -> TraceWriter:
    """
    Get global writer instance (singleton).

    Args:
        db_path: Optional database path

    Returns:
        TraceWriter instance
    """
    global _global_writer

    with _global_writer_lock:
        if _global_writer is None:
            _global_writer = TraceWriter(db_path)
            _global_writer.start()

        return _global_writer


def reset_writer() -> None:
    """Reset global writer (for testing)."""
    global _global_writer

    with _global_writer_lock:
        if _global_writer is not None:
            _global_writer.stop()
            _global_writer = None
