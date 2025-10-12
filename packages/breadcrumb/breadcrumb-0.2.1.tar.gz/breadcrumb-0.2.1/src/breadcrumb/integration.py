"""
Integration layer connecting instrumentation backend to storage.

This module bridges the gap between the PEP 669 instrumentation backend
(which captures events in memory) and the storage layer (which persists
events to the database).

Architecture:
- Backend captures TraceEvent objects in thread-local storage
- Integration layer periodically pulls events from backend
- Events are converted and written to database via TraceWriter
- Trace records are created/updated automatically

Usage:
    import breadcrumb
    breadcrumb.init()  # Starts both backend and storage integration

    # Your code here - events automatically captured and persisted

    breadcrumb.shutdown()  # Graceful shutdown
"""

import threading
import time
import uuid
import atexit
from typing import Optional
from datetime import datetime, timezone

from breadcrumb.instrumentation.pep669_backend import PEP669Backend, TraceEvent
from breadcrumb.storage.async_writer import TraceWriter, get_writer


class TracingIntegration:
    """
    Integration layer between backend and storage.

    Responsibilities:
    - Receive events from backend via callback
    - Create trace records for new traces
    - Write events to database
    - Manage trace lifecycle (started_at, ended_at, status)
    - Handle exceptions properly
    """

    def __init__(
        self,
        backend: PEP669Backend,
        writer: Optional[TraceWriter] = None,
        db_path: Optional[str] = None,
    ):
        """
        Initialize integration layer.

        Args:
            backend: PEP 669 backend instance
            writer: TraceWriter instance (or creates one)
            db_path: Database path (if writer not provided)
        """
        self.backend = backend

        # Create writer with backend reference for diagnostics
        if writer is None:
            writer = TraceWriter(
                db_path=db_path,
                backend_ref=backend,  # Pass backend reference for diagnostic reports
            )
            writer.start()

        self.writer = writer

        # Integration state
        self._running = False

        # Track active traces (thread_id -> trace_id)
        self._active_traces: dict[int, str] = {}
        self._lock = threading.Lock()

        # Register shutdown hook
        atexit.register(self.stop)

        # Register event callback with backend
        # Note: We can't set this in __init__ because the backend may already be created
        # So we'll set it when start() is called

    def start(self) -> None:
        """Start integration layer."""
        if self._running:
            return

        # Register callback with backend
        self.backend.event_callback = self._on_event

        # Start backend
        if not self.backend.is_active():
            self.backend.start()

        self._running = True

    def stop(self, timeout: float = 5.0) -> None:
        """
        Stop integration layer and flush remaining events.

        Args:
            timeout: Maximum time to wait for flush (seconds)
        """
        if not self._running:
            return

        self._running = False

        # Mark all active traces as completed
        with self._lock:
            active_traces = list(self._active_traces.values())

        for trace_id in active_traces:
            self._update_trace_status(trace_id, 'completed')

        # Stop backend
        if self.backend.is_active():
            self.backend.stop()

        # Stop writer (this flushes remaining events, including trace updates)
        self.writer.stop(timeout=timeout)

        # Clear active traces
        with self._lock:
            self._active_traces.clear()

    def _on_event(self, event: TraceEvent) -> None:
        """
        Event callback - called by backend for each captured event.

        Args:
            event: TraceEvent from backend
        """
        try:
            # Get or create trace for this thread
            trace_id = self._get_or_create_trace(event.thread_id, event.timestamp)

            # Build event data dict
            event_data = {}
            if event.args:
                event_data['args'] = event.args
            if event.kwargs:
                event_data['kwargs'] = event.kwargs
            if event.return_value is not None:
                event_data['return_value'] = event.return_value
            if event.local_vars:
                event_data['local_vars'] = event.local_vars
            if event.is_async:
                event_data['is_async'] = True
            # For call_site events, include caller information for gap detection
            if event.event_type == 'call_site':
                if event.called_from_function:
                    event_data['called_from_function'] = event.called_from_function
                if event.called_from_module:
                    event_data['called_from_module'] = event.called_from_module

            # Write trace event
            event_id = str(uuid.uuid4())
            self.writer.write_trace_event(
                event_id=event_id,
                trace_id=trace_id,
                timestamp=event.timestamp,
                event_type=event.event_type,
                function_name=event.function_name,
                module_name=event.module_name,
                file_path=event.file_path,
                line_number=event.line_number,
                data=event_data if event_data else None,
            )

            # If this is an exception event, write exception record
            if event.event_type == 'exception' and event.exception_type:
                exception_id = str(uuid.uuid4())
                self.writer.write_exception(
                    exception_id=exception_id,
                    event_id=event_id,
                    trace_id=trace_id,
                    exception_type=event.exception_type,
                    message=event.exception_message or "",
                    stack_trace=event.exception_traceback,
                )
                # Update trace status
                self._update_trace_status(trace_id, 'failed')

        except Exception as e:
            # Don't crash instrumentation if integration fails
            import sys
            print(f"ERROR: Integration event handler failed: {e}", file=sys.stderr)

    def _get_or_create_trace(self, thread_id: int, started_at: datetime) -> str:
        """
        Get existing trace for thread or create a new one.

        Args:
            thread_id: Thread ID
            started_at: Timestamp of first event

        Returns:
            Trace ID
        """
        with self._lock:
            # Check if we have an active trace for this thread
            if thread_id in self._active_traces:
                return self._active_traces[thread_id]

            # Create new trace
            trace_id = str(uuid.uuid4())
            self._active_traces[thread_id] = trace_id

            # Write trace record
            self.writer.write_trace(
                trace_id=trace_id,
                started_at=started_at,
                status='running',
                thread_id=thread_id,
            )

            return trace_id

    def _update_trace_status(self, trace_id: str, status: str) -> None:
        """
        Update trace status.

        Args:
            trace_id: Trace ID
            status: New status ('running', 'completed', 'failed')
        """
        # Update trace with new status and end time
        ended_at = datetime.now(timezone.utc) if status in ('completed', 'failed') else None
        self.writer.update_trace(
            trace_id=trace_id,
            ended_at=ended_at,
            status=status,
        )


# Global integration instance
_global_integration: Optional[TracingIntegration] = None
_global_integration_lock = threading.Lock()


def get_integration() -> Optional[TracingIntegration]:
    """
    Get global integration instance.

    Returns:
        TracingIntegration instance if initialized, None otherwise
    """
    return _global_integration


def start_integration(
    backend: PEP669Backend,
    writer: Optional[TraceWriter] = None,
    db_path: Optional[str] = None,
) -> TracingIntegration:
    """
    Start global integration layer.

    Args:
        backend: PEP 669 backend instance
        writer: Optional TraceWriter instance
        db_path: Optional database path

    Returns:
        TracingIntegration instance
    """
    global _global_integration

    with _global_integration_lock:
        if _global_integration is not None:
            raise RuntimeError("Integration already started")

        _global_integration = TracingIntegration(
            backend=backend,
            writer=writer,
            db_path=db_path,
        )
        _global_integration.start()

        return _global_integration


def stop_integration() -> None:
    """Stop global integration layer."""
    global _global_integration

    with _global_integration_lock:
        if _global_integration is not None:
            _global_integration.stop()
            _global_integration = None


def reset_integration() -> None:
    """Reset integration (for testing)."""
    stop_integration()
