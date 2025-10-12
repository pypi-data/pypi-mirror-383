"""
Tests for CLI get command.

Validates:
- Successful trace retrieval
- JSON and table output formats
- Trace not found error handling
- Invalid trace ID handling
- Exit codes
"""

import pytest
import tempfile
import os
from datetime import datetime, timezone
import uuid
from io import StringIO
import sys

from breadcrumb.cli.commands.get import execute_get, EXIT_SUCCESS, EXIT_ERROR, EXIT_NO_RESULTS
from breadcrumb.storage.connection import reset_manager
from breadcrumb.storage.async_writer import TraceWriter


@pytest.fixture
def temp_db_path():
    """Create a temporary database path."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = os.path.join(tmpdir, ".breadcrumb", "traces.duckdb")
        yield db_path


@pytest.fixture(autouse=True)
def cleanup():
    """Reset global instances."""
    reset_manager()
    yield
    # Ensure manager is closed before cleanup
    try:
        from breadcrumb.storage.connection import _global_manager
        if _global_manager is not None:
            _global_manager.close()
    except:
        pass
    reset_manager()


@pytest.fixture
def populated_db(temp_db_path):
    """Create database with sample trace data."""
    writer = TraceWriter(db_path=temp_db_path, batch_size=1)
    writer.start()

    # Create a trace with events and an exception
    trace_id = str(uuid.uuid4())
    event_id1 = str(uuid.uuid4())
    event_id2 = str(uuid.uuid4())
    exception_id = str(uuid.uuid4())

    # Write trace
    writer.write_trace(
        trace_id=trace_id,
        started_at=datetime.now(timezone.utc),
        status='failed',
        thread_id=12345,
        metadata='{"test": "data"}'
    )

    # Write events
    writer.write_trace_event(
        event_id=event_id1,
        trace_id=trace_id,
        timestamp=datetime.now(timezone.utc),
        event_type='call',
        function_name='test_function',
        module_name='test_module',
        file_path='/path/to/test.py',
        line_number=42
    )

    writer.write_trace_event(
        event_id=event_id2,
        trace_id=trace_id,
        timestamp=datetime.now(timezone.utc),
        event_type='exception',
        function_name='test_function',
        module_name='test_module'
    )

    # Write exception
    writer.write_exception(
        exception_id=exception_id,
        event_id=event_id2,
        trace_id=trace_id,
        exception_type='ValueError',
        message='Test error message',
        stack_trace='Traceback (most recent call last):\n  File "test.py", line 42\nValueError: Test error message'
    )

    import time
    time.sleep(0.2)
    writer.stop()

    return trace_id, temp_db_path


class TestGetCommandSuccess:
    """Test successful trace retrieval."""

    def test_get_trace_json_format(self, populated_db):
        """Test getting trace with JSON format."""
        trace_id, db_path = populated_db

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            exit_code = execute_get(
                trace_id=trace_id,
                format="json",
                db_path=db_path,
                verbose=False
            )

            output = captured_output.getvalue()
        finally:
            sys.stdout = sys.__stdout__

        assert exit_code == EXIT_SUCCESS
        assert trace_id in output
        assert 'trace' in output
        assert 'events' in output
        assert 'exceptions' in output
        assert 'summary' in output

        # Verify it's valid JSON
        import json
        data = json.loads(output)
        assert data['trace']['id'] == trace_id
        assert data['summary']['trace_id'] == trace_id
        assert data['summary']['status'] == 'failed'
        assert data['summary']['event_count'] >= 2
        assert data['summary']['exception_count'] >= 1

    def test_get_trace_table_format(self, populated_db):
        """Test getting trace with table format."""
        trace_id, db_path = populated_db

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            exit_code = execute_get(
                trace_id=trace_id,
                format="table",
                db_path=db_path,
                verbose=False
            )

            output = captured_output.getvalue()
        finally:
            sys.stdout = sys.__stdout__

        assert exit_code == EXIT_SUCCESS
        assert 'TRACE DETAILS' in output
        assert 'EVENTS' in output
        assert 'EXCEPTIONS' in output
        assert trace_id in output
        assert 'failed' in output.lower()
        assert 'ValueError' in output
        assert 'Test error message' in output

    def test_get_trace_verbose(self, populated_db):
        """Test getting trace with verbose output."""
        trace_id, db_path = populated_db

        # Capture both stdout and stderr
        captured_stdout = StringIO()
        captured_stderr = StringIO()
        sys.stdout = captured_stdout
        sys.stderr = captured_stderr

        try:
            exit_code = execute_get(
                trace_id=trace_id,
                format="json",
                db_path=db_path,
                verbose=True
            )

            stdout_output = captured_stdout.getvalue()
            stderr_output = captured_stderr.getvalue()
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

        assert exit_code == EXIT_SUCCESS
        # Verbose output should show info in stderr
        assert trace_id in stderr_output or trace_id in stdout_output
        assert 'events' in stderr_output.lower() or 'events' in stdout_output


class TestGetCommandErrors:
    """Test error handling."""

    def test_trace_not_found(self, temp_db_path):
        """Test getting a non-existent trace."""
        # Initialize database with no traces
        writer = TraceWriter(db_path=temp_db_path, batch_size=1)
        writer.start()
        import time
        time.sleep(0.1)
        writer.stop()

        fake_trace_id = "00000000-0000-0000-0000-000000000000"

        # Capture stderr
        captured_stderr = StringIO()
        captured_stdout = StringIO()
        sys.stderr = captured_stderr
        sys.stdout = captured_stdout

        try:
            exit_code = execute_get(
                trace_id=fake_trace_id,
                format="json",
                db_path=temp_db_path,
                verbose=False
            )

            stderr_output = captured_stderr.getvalue()
        finally:
            sys.stderr = sys.__stderr__
            sys.stdout = sys.__stdout__

        # Should return EXIT_NO_RESULTS (2) for trace not found
        assert exit_code == EXIT_NO_RESULTS
        assert 'TraceNotFoundError' in stderr_output
        assert fake_trace_id in stderr_output

    def test_trace_not_found_table_format(self, temp_db_path):
        """Test getting a non-existent trace with table format."""
        # Initialize database with no traces
        writer = TraceWriter(db_path=temp_db_path, batch_size=1)
        writer.start()
        import time
        time.sleep(0.1)
        writer.stop()

        fake_trace_id = "11111111-1111-1111-1111-111111111111"

        # Capture stderr
        captured_stderr = StringIO()
        captured_stdout = StringIO()
        sys.stderr = captured_stderr
        sys.stdout = captured_stdout

        try:
            exit_code = execute_get(
                trace_id=fake_trace_id,
                format="table",
                db_path=temp_db_path,
                verbose=False
            )

            stderr_output = captured_stderr.getvalue()
        finally:
            sys.stderr = sys.__stderr__
            sys.stdout = sys.__stdout__

        # Should return EXIT_NO_RESULTS (2) for trace not found
        assert exit_code == EXIT_NO_RESULTS
        # Error message should be human-readable for table format
        assert 'ERROR' in stderr_output or 'error' in stderr_output.lower()
        assert fake_trace_id in stderr_output

    def test_invalid_database_path(self):
        """Test with invalid database path."""
        fake_trace_id = str(uuid.uuid4())

        # Capture stderr
        captured_stderr = StringIO()
        captured_stdout = StringIO()
        sys.stderr = captured_stderr
        sys.stdout = captured_stdout

        try:
            exit_code = execute_get(
                trace_id=fake_trace_id,
                format="json",
                db_path="/nonexistent/path/traces.duckdb",
                verbose=False
            )

            stderr_output = captured_stderr.getvalue()
        finally:
            sys.stderr = sys.__stderr__
            sys.stdout = sys.__stdout__

        # With invalid database, trace won't be found (returns EXIT_NO_RESULTS)
        # or there might be a database error (returns EXIT_ERROR)
        assert exit_code in [EXIT_ERROR, EXIT_NO_RESULTS]
        assert 'error' in stderr_output.lower() or 'not found' in stderr_output.lower()


class TestGetCommandExitCodes:
    """Test exit code behavior."""

    def test_exit_codes_defined(self):
        """Test that exit codes are defined correctly."""
        assert EXIT_SUCCESS == 0
        assert EXIT_ERROR == 1
        assert EXIT_NO_RESULTS == 2

    def test_success_returns_zero(self, populated_db):
        """Test that successful get returns EXIT_SUCCESS."""
        trace_id, db_path = populated_db

        # Capture stdout to suppress output
        captured_stdout = StringIO()
        sys.stdout = captured_stdout

        try:
            exit_code = execute_get(
                trace_id=trace_id,
                format="json",
                db_path=db_path,
                verbose=False
            )
        finally:
            sys.stdout = sys.__stdout__

        assert exit_code == EXIT_SUCCESS

    def test_not_found_returns_two(self, temp_db_path):
        """Test that trace not found returns EXIT_NO_RESULTS."""
        # Initialize database
        writer = TraceWriter(db_path=temp_db_path, batch_size=1)
        writer.start()
        import time
        time.sleep(0.1)
        writer.stop()

        # Capture output to suppress
        captured_stdout = StringIO()
        captured_stderr = StringIO()
        sys.stdout = captured_stdout
        sys.stderr = captured_stderr

        try:
            exit_code = execute_get(
                trace_id="00000000-0000-0000-0000-000000000000",
                format="json",
                db_path=temp_db_path,
                verbose=False
            )
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

        assert exit_code == EXIT_NO_RESULTS


class TestGetCommandDataValidation:
    """Test data validation and output completeness."""

    def test_get_includes_all_fields(self, populated_db):
        """Test that get includes all expected fields."""
        trace_id, db_path = populated_db

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            exit_code = execute_get(
                trace_id=trace_id,
                format="json",
                db_path=db_path,
                verbose=False
            )

            output = captured_output.getvalue()
        finally:
            sys.stdout = sys.__stdout__

        import json
        data = json.loads(output)

        # Verify trace fields
        assert 'trace' in data
        assert data['trace']['id'] == trace_id
        assert 'status' in data['trace']
        assert 'started_at' in data['trace']

        # Verify events
        assert 'events' in data
        assert isinstance(data['events'], list)
        assert len(data['events']) >= 2

        # Verify at least one event has expected fields
        event = data['events'][0]
        assert 'event_type' in event
        assert 'function_name' in event
        assert 'timestamp' in event

        # Verify exceptions
        assert 'exceptions' in data
        assert isinstance(data['exceptions'], list)
        assert len(data['exceptions']) >= 1

        # Verify at least one exception has expected fields
        exc = data['exceptions'][0]
        assert 'exception_type' in exc
        assert 'message' in exc
        assert exc['exception_type'] == 'ValueError'
        assert exc['message'] == 'Test error message'

        # Verify summary
        assert 'summary' in data
        assert data['summary']['trace_id'] == trace_id
        assert data['summary']['event_count'] >= 2
        assert data['summary']['exception_count'] >= 1

    def test_get_table_format_sections(self, populated_db):
        """Test that table format includes all sections."""
        trace_id, db_path = populated_db

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            exit_code = execute_get(
                trace_id=trace_id,
                format="table",
                db_path=db_path,
                verbose=False
            )

            output = captured_output.getvalue()
        finally:
            sys.stdout = sys.__stdout__

        # Verify all major sections are present
        assert 'TRACE DETAILS' in output
        assert 'EVENTS' in output
        assert 'EXCEPTIONS' in output

        # Verify key data is displayed
        assert trace_id in output
        assert 'failed' in output.lower()
        assert 'test_function' in output
        assert 'ValueError' in output
        assert 'Test error message' in output

        # Verify stack trace is shown
        assert 'STACK TRACE' in output or 'Traceback' in output
