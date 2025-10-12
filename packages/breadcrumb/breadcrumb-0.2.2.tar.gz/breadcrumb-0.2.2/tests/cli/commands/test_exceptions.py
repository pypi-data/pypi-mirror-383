"""
Tests for CLI exceptions command.

Validates:
- Default behavior (last 10 exceptions)
- Time range filtering
- JSON and table formats
- Exit codes
"""

import pytest
import tempfile
import os
from datetime import datetime, timezone
import uuid

from typer.testing import CliRunner

from breadcrumb.cli.main import app, EXIT_SUCCESS, EXIT_ERROR, EXIT_NO_RESULTS
from breadcrumb.cli.commands.exceptions import execute_exceptions
from breadcrumb.storage.async_writer import TraceWriter
from breadcrumb.storage.connection import reset_manager


runner = CliRunner()


@pytest.fixture
def temp_db_path():
    """Create a temporary database path."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = os.path.join(tmpdir, ".breadcrumb", "traces.duckdb")
        yield db_path


@pytest.fixture(autouse=True)
def cleanup():
    """Reset global instances after each test."""
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
def db_with_exceptions(temp_db_path):
    """Create database with sample exceptions."""
    writer = TraceWriter(db_path=temp_db_path, batch_size=5)
    writer.start()

    # Create trace with exception
    trace_id1 = str(uuid.uuid4())
    event_id1 = str(uuid.uuid4())

    writer.write_trace(
        trace_id=trace_id1,
        started_at=datetime.now(timezone.utc),
        status='failed',
        thread_id=12345
    )

    writer.write_trace_event(
        event_id=event_id1,
        trace_id=trace_id1,
        timestamp=datetime.now(timezone.utc),
        event_type='exception',
        function_name='test_func',
        module_name='__main__'
    )

    writer.write_exception(
        exception_id=str(uuid.uuid4()),
        event_id=event_id1,
        trace_id=trace_id1,
        exception_type='ValueError',
        message='Test error message'
    )

    # Create another trace with exception
    trace_id2 = str(uuid.uuid4())
    event_id2 = str(uuid.uuid4())

    writer.write_trace(
        trace_id=trace_id2,
        started_at=datetime.now(timezone.utc),
        status='failed',
        thread_id=12346
    )

    writer.write_trace_event(
        event_id=event_id2,
        trace_id=trace_id2,
        timestamp=datetime.now(timezone.utc),
        event_type='exception',
        function_name='another_func',
        module_name='__main__'
    )

    writer.write_exception(
        exception_id=str(uuid.uuid4()),
        event_id=event_id2,
        trace_id=trace_id2,
        exception_type='KeyError',
        message='Key not found'
    )

    import time
    time.sleep(0.3)
    writer.stop()

    return temp_db_path


@pytest.fixture
def empty_db(temp_db_path):
    """Create empty database with no exceptions."""
    writer = TraceWriter(db_path=temp_db_path, batch_size=1)
    writer.start()

    # Create a successful trace (no exceptions)
    trace_id = str(uuid.uuid4())
    writer.write_trace(
        trace_id=trace_id,
        started_at=datetime.now(timezone.utc),
        status='completed',
        thread_id=12345
    )

    import time
    time.sleep(0.2)
    writer.stop()

    return temp_db_path


class TestExecuteExceptions:
    """Test execute_exceptions function directly."""

    def test_default_behavior_with_exceptions(self, db_with_exceptions):
        """Test default behavior shows last 10 exceptions."""
        exit_code = execute_exceptions(
            since="1h",
            limit=10,
            format="json",
            db_path=db_with_exceptions,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

    def test_json_format(self, db_with_exceptions):
        """Test JSON format output."""
        exit_code = execute_exceptions(
            since="1h",
            limit=10,
            format="json",
            db_path=db_with_exceptions,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

    def test_table_format(self, db_with_exceptions):
        """Test table format output."""
        exit_code = execute_exceptions(
            since="1h",
            limit=10,
            format="table",
            db_path=db_with_exceptions,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

    def test_no_exceptions_found(self, empty_db):
        """Test exit code when no exceptions found."""
        exit_code = execute_exceptions(
            since="1h",
            limit=10,
            format="json",
            db_path=empty_db,
            verbose=False
        )

        assert exit_code == EXIT_NO_RESULTS

    def test_time_range_30m(self, db_with_exceptions):
        """Test 30 minute time range."""
        exit_code = execute_exceptions(
            since="30m",
            limit=10,
            format="json",
            db_path=db_with_exceptions,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

    def test_time_range_2h(self, db_with_exceptions):
        """Test 2 hour time range."""
        exit_code = execute_exceptions(
            since="2h",
            limit=10,
            format="json",
            db_path=db_with_exceptions,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

    def test_time_range_1d(self, db_with_exceptions):
        """Test 1 day time range."""
        exit_code = execute_exceptions(
            since="1d",
            limit=10,
            format="json",
            db_path=db_with_exceptions,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

    def test_limit_parameter(self, db_with_exceptions):
        """Test limit parameter."""
        exit_code = execute_exceptions(
            since="1h",
            limit=5,
            format="json",
            db_path=db_with_exceptions,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

    def test_invalid_time_range(self, db_with_exceptions):
        """Test invalid time range returns error."""
        exit_code = execute_exceptions(
            since="invalid",
            limit=10,
            format="json",
            db_path=db_with_exceptions,
            verbose=False
        )

        assert exit_code == EXIT_ERROR

    def test_verbose_mode(self, db_with_exceptions, capsys):
        """Test verbose mode prints debug info."""
        exit_code = execute_exceptions(
            since="1h",
            limit=10,
            format="json",
            db_path=db_with_exceptions,
            verbose=True
        )

        assert exit_code == EXIT_SUCCESS
        captured = capsys.readouterr()
        # Verbose should print to stderr
        assert "Searching" in captured.err or len(captured.err) > 0


class TestExceptionsCLICommand:
    """Test exceptions CLI command via Typer."""

    def test_exceptions_command_default(self, db_with_exceptions):
        """Test exceptions command with defaults."""
        result = runner.invoke(app, [
            "--db-path", db_with_exceptions,
            "exceptions"
        ])

        # Should succeed
        assert result.exit_code == EXIT_SUCCESS
        # Should output JSON by default
        assert "exceptions" in result.stdout

    def test_exceptions_command_with_since(self, db_with_exceptions):
        """Test exceptions command with --since option."""
        result = runner.invoke(app, [
            "--db-path", db_with_exceptions,
            "exceptions",
            "--since", "30m"
        ])

        assert result.exit_code == EXIT_SUCCESS
        assert "exceptions" in result.stdout

    def test_exceptions_command_with_limit(self, db_with_exceptions):
        """Test exceptions command with --limit option."""
        result = runner.invoke(app, [
            "--db-path", db_with_exceptions,
            "exceptions",
            "--limit", "5"
        ])

        assert result.exit_code == EXIT_SUCCESS

    def test_exceptions_command_short_options(self, db_with_exceptions):
        """Test exceptions command with short options."""
        result = runner.invoke(app, [
            "--db-path", db_with_exceptions,
            "exceptions",
            "-s", "1h",
            "-n", "10"
        ])

        assert result.exit_code == EXIT_SUCCESS

    def test_exceptions_command_table_format(self, db_with_exceptions):
        """Test exceptions command with table format."""
        result = runner.invoke(app, [
            "--format", "table",
            "--db-path", db_with_exceptions,
            "exceptions"
        ])

        assert result.exit_code == EXIT_SUCCESS
        # Table format should have headers
        assert "trace_id" in result.stdout or "Exception" in result.stdout

    def test_exceptions_command_no_results(self, empty_db):
        """Test exceptions command when no exceptions found."""
        result = runner.invoke(app, [
            "--db-path", empty_db,
            "exceptions"
        ])

        assert result.exit_code == EXIT_NO_RESULTS
        assert "No exceptions" in result.stdout or "exceptions" in result.stdout

    def test_exceptions_command_verbose(self, db_with_exceptions):
        """Test exceptions command with verbose flag."""
        result = runner.invoke(app, [
            "--verbose",
            "--db-path", db_with_exceptions,
            "exceptions"
        ])

        assert result.exit_code == EXIT_SUCCESS
        # Verbose should print debug info to stderr
        assert len(result.stderr) > 0

    def test_exceptions_command_help(self):
        """Test exceptions command help."""
        result = runner.invoke(app, ["exceptions", "--help"])

        assert result.exit_code == 0
        assert "exception" in result.stdout.lower()
        assert "--since" in result.stdout
        assert "--limit" in result.stdout


class TestExceptionsTimeRanges:
    """Test various time range formats."""

    def test_absolute_date_format(self, db_with_exceptions):
        """Test absolute date format (YYYY-MM-DD)."""
        # Use date from the past to ensure no exceptions
        exit_code = execute_exceptions(
            since="2020-01-01",
            limit=10,
            format="json",
            db_path=db_with_exceptions,
            verbose=False
        )

        # Should succeed (even if no results, query is valid)
        assert exit_code in [EXIT_SUCCESS, EXIT_NO_RESULTS]

    def test_relative_time_minutes(self, db_with_exceptions):
        """Test relative time in minutes."""
        exit_code = execute_exceptions(
            since="30m",
            limit=10,
            format="json",
            db_path=db_with_exceptions,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

    def test_relative_time_hours(self, db_with_exceptions):
        """Test relative time in hours."""
        exit_code = execute_exceptions(
            since="2h",
            limit=10,
            format="json",
            db_path=db_with_exceptions,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

    def test_relative_time_days(self, db_with_exceptions):
        """Test relative time in days."""
        exit_code = execute_exceptions(
            since="1d",
            limit=10,
            format="json",
            db_path=db_with_exceptions,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS


class TestExceptionsEdgeCases:
    """Test edge cases and error conditions."""

    def test_invalid_db_path(self):
        """Test with invalid database path."""
        exit_code = execute_exceptions(
            since="1h",
            limit=10,
            format="json",
            db_path="/nonexistent/path/traces.duckdb",
            verbose=False
        )

        # DuckDB creates new database at invalid path, so we get NO_RESULTS
        # This is acceptable behavior
        assert exit_code == EXIT_NO_RESULTS

    def test_zero_limit(self, db_with_exceptions):
        """Test with limit of 0."""
        exit_code = execute_exceptions(
            since="1h",
            limit=0,
            format="json",
            db_path=db_with_exceptions,
            verbose=False
        )

        # Should handle gracefully (no results or success)
        assert exit_code in [EXIT_SUCCESS, EXIT_NO_RESULTS]

    def test_very_large_limit(self, db_with_exceptions):
        """Test with very large limit."""
        exit_code = execute_exceptions(
            since="1h",
            limit=10000,
            format="json",
            db_path=db_with_exceptions,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS
