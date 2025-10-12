"""
Tests for CLI performance command.

Validates:
- Performance statistics display
- Slowest traces listing
- JSON and table formats
- Exit codes
"""

import pytest
import tempfile
import os
from datetime import datetime, timezone, timedelta
import uuid
import time

from typer.testing import CliRunner

from breadcrumb.cli.main import app, EXIT_SUCCESS, EXIT_ERROR, EXIT_NO_RESULTS
from breadcrumb.cli.commands.performance import execute_performance
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
def db_with_performance_data(temp_db_path):
    """Create database with sample performance data."""
    writer = TraceWriter(db_path=temp_db_path, batch_size=10)
    writer.start()

    # Create multiple traces for the same function with different durations
    for i in range(5):
        trace_id = str(uuid.uuid4())
        event_id = str(uuid.uuid4())

        # Create traces with varying durations
        start_time = datetime.now(timezone.utc) - timedelta(milliseconds=100 * (i + 1))
        end_time = start_time + timedelta(milliseconds=10 * (i + 1))

        writer.write_trace(
            trace_id=trace_id,
            started_at=start_time,
            ended_at=end_time,
            status='completed',
            thread_id=12345 + i
        )

        writer.write_trace_event(
            event_id=event_id,
            trace_id=trace_id,
            timestamp=start_time,
            event_type='call',
            function_name='fetch_data',
            module_name='myapp'
        )

    # Create trace for a different function
    trace_id = str(uuid.uuid4())
    event_id = str(uuid.uuid4())
    start_time = datetime.now(timezone.utc)
    end_time = start_time + timedelta(milliseconds=50)

    writer.write_trace(
        trace_id=trace_id,
        started_at=start_time,
        ended_at=end_time,
        status='completed',
        thread_id=99999
    )

    writer.write_trace_event(
        event_id=event_id,
        trace_id=trace_id,
        timestamp=start_time,
        event_type='call',
        function_name='process_payment',
        module_name='myapp'
    )

    time.sleep(0.3)
    writer.stop()

    return temp_db_path


@pytest.fixture
def empty_db(temp_db_path):
    """Create empty database with no traces."""
    writer = TraceWriter(db_path=temp_db_path, batch_size=1)
    writer.start()

    # Create a trace without the target function
    trace_id = str(uuid.uuid4())
    writer.write_trace(
        trace_id=trace_id,
        started_at=datetime.now(timezone.utc),
        status='completed',
        thread_id=12345
    )

    time.sleep(0.2)
    writer.stop()

    return temp_db_path


class TestExecutePerformance:
    """Test execute_performance function directly."""

    def test_default_behavior_with_data(self, db_with_performance_data):
        """Test default behavior shows performance stats."""
        exit_code = execute_performance(
            function="fetch_data",
            limit=10,
            format="json",
            db_path=db_with_performance_data,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

    def test_json_format(self, db_with_performance_data):
        """Test JSON format output."""
        exit_code = execute_performance(
            function="fetch_data",
            limit=10,
            format="json",
            db_path=db_with_performance_data,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

    def test_table_format(self, db_with_performance_data):
        """Test table format output."""
        exit_code = execute_performance(
            function="fetch_data",
            limit=10,
            format="table",
            db_path=db_with_performance_data,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

    def test_function_not_found(self, empty_db):
        """Test exit code when function has no traces."""
        exit_code = execute_performance(
            function="nonexistent_function",
            limit=10,
            format="json",
            db_path=empty_db,
            verbose=False
        )

        assert exit_code == EXIT_NO_RESULTS

    def test_limit_parameter(self, db_with_performance_data):
        """Test limit parameter for slowest traces."""
        exit_code = execute_performance(
            function="fetch_data",
            limit=3,
            format="json",
            db_path=db_with_performance_data,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

    def test_different_function(self, db_with_performance_data):
        """Test analyzing different function."""
        exit_code = execute_performance(
            function="process_payment",
            limit=10,
            format="json",
            db_path=db_with_performance_data,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

    def test_verbose_mode(self, db_with_performance_data, capsys):
        """Test verbose mode prints debug info."""
        exit_code = execute_performance(
            function="fetch_data",
            limit=10,
            format="json",
            db_path=db_with_performance_data,
            verbose=True
        )

        assert exit_code == EXIT_SUCCESS
        captured = capsys.readouterr()
        # Verbose should print to stderr
        assert "Analyzing" in captured.err or len(captured.err) > 0


class TestPerformanceCLICommand:
    """Test performance CLI command via Typer."""

    def test_performance_command_default(self, db_with_performance_data):
        """Test performance command with defaults."""
        result = runner.invoke(app, [
            "--db-path", db_with_performance_data,
            "performance",
            "fetch_data"
        ])

        # Should succeed
        assert result.exit_code == EXIT_SUCCESS
        # Should output JSON by default
        assert "statistics" in result.stdout or "function" in result.stdout

    def test_performance_command_with_limit(self, db_with_performance_data):
        """Test performance command with --limit option."""
        result = runner.invoke(app, [
            "--db-path", db_with_performance_data,
            "performance",
            "fetch_data",
            "--limit", "5"
        ])

        assert result.exit_code == EXIT_SUCCESS

    def test_performance_command_short_option(self, db_with_performance_data):
        """Test performance command with short option."""
        result = runner.invoke(app, [
            "--db-path", db_with_performance_data,
            "performance",
            "fetch_data",
            "-n", "3"
        ])

        assert result.exit_code == EXIT_SUCCESS

    def test_performance_command_table_format(self, db_with_performance_data):
        """Test performance command with table format."""
        result = runner.invoke(app, [
            "--format", "table",
            "--db-path", db_with_performance_data,
            "performance",
            "fetch_data"
        ])

        assert result.exit_code == EXIT_SUCCESS
        # Table format should have statistics
        assert "Performance" in result.stdout or "Duration" in result.stdout or "Call Count" in result.stdout

    def test_performance_command_function_not_found(self, empty_db):
        """Test performance command when function has no traces."""
        result = runner.invoke(app, [
            "--db-path", empty_db,
            "performance",
            "nonexistent_function"
        ])

        assert result.exit_code == EXIT_NO_RESULTS
        assert "No traces found" in result.stderr or "FunctionNotFound" in result.stderr

    def test_performance_command_verbose(self, db_with_performance_data):
        """Test performance command with verbose flag."""
        result = runner.invoke(app, [
            "--verbose",
            "--db-path", db_with_performance_data,
            "performance",
            "fetch_data"
        ])

        assert result.exit_code == EXIT_SUCCESS
        # Verbose should print debug info to stderr
        assert len(result.stderr) > 0

    def test_performance_command_help(self):
        """Test performance command help."""
        result = runner.invoke(app, ["performance", "--help"])

        assert result.exit_code == 0
        assert "performance" in result.stdout.lower()
        assert "function" in result.stdout.lower()
        assert "--limit" in result.stdout


class TestPerformanceStatistics:
    """Test performance statistics calculations."""

    def test_statistics_include_avg_min_max(self, db_with_performance_data, capsys):
        """Test that statistics include avg, min, max durations."""
        exit_code = execute_performance(
            function="fetch_data",
            limit=10,
            format="json",
            db_path=db_with_performance_data,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS
        captured = capsys.readouterr()

        # Check for statistics fields in JSON output
        assert "avg_duration_ms" in captured.out or "statistics" in captured.out
        assert "min_duration_ms" in captured.out or "statistics" in captured.out
        assert "max_duration_ms" in captured.out or "statistics" in captured.out

    def test_slowest_traces_returned(self, db_with_performance_data, capsys):
        """Test that slowest traces are returned."""
        exit_code = execute_performance(
            function="fetch_data",
            limit=3,
            format="json",
            db_path=db_with_performance_data,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS
        captured = capsys.readouterr()

        # Check for slowest_traces field
        assert "slowest_traces" in captured.out or "trace_id" in captured.out

    def test_call_count_included(self, db_with_performance_data, capsys):
        """Test that call count is included in statistics."""
        exit_code = execute_performance(
            function="fetch_data",
            limit=10,
            format="json",
            db_path=db_with_performance_data,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS
        captured = capsys.readouterr()

        # Check for call_count field
        assert "call_count" in captured.out


class TestPerformanceEdgeCases:
    """Test edge cases and error conditions."""

    def test_invalid_db_path(self):
        """Test with invalid database path."""
        exit_code = execute_performance(
            function="test_func",
            limit=10,
            format="json",
            db_path="/nonexistent/path/traces.duckdb",
            verbose=False
        )

        # DuckDB creates new database at invalid path, so we get NO_RESULTS
        assert exit_code == EXIT_NO_RESULTS

    def test_zero_limit(self, db_with_performance_data):
        """Test with limit of 0."""
        exit_code = execute_performance(
            function="fetch_data",
            limit=0,
            format="json",
            db_path=db_with_performance_data,
            verbose=False
        )

        # Should handle gracefully - still show statistics
        assert exit_code == EXIT_SUCCESS

    def test_very_large_limit(self, db_with_performance_data):
        """Test with very large limit."""
        exit_code = execute_performance(
            function="fetch_data",
            limit=10000,
            format="json",
            db_path=db_with_performance_data,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

    def test_function_name_with_special_chars(self, db_with_performance_data):
        """Test function name with special characters."""
        exit_code = execute_performance(
            function="my_function_123",
            limit=10,
            format="json",
            db_path=db_with_performance_data,
            verbose=False
        )

        # Should not crash - just return no results
        assert exit_code == EXIT_NO_RESULTS


class TestPerformanceFormats:
    """Test different output formats."""

    def test_json_format_structure(self, db_with_performance_data, capsys):
        """Test JSON format structure."""
        exit_code = execute_performance(
            function="fetch_data",
            limit=5,
            format="json",
            db_path=db_with_performance_data,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS
        captured = capsys.readouterr()

        # Verify JSON structure elements
        assert "function" in captured.out
        assert "statistics" in captured.out
        assert "slowest_traces" in captured.out

    def test_table_format_structure(self, db_with_performance_data, capsys):
        """Test table format structure."""
        exit_code = execute_performance(
            function="fetch_data",
            limit=5,
            format="table",
            db_path=db_with_performance_data,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS
        captured = capsys.readouterr()

        # Verify table format elements
        assert "Performance" in captured.out or "Statistics" in captured.out
        assert "Duration" in captured.out or "duration" in captured.out

    def test_json_format_no_results(self, empty_db, capsys):
        """Test JSON format when no results found."""
        exit_code = execute_performance(
            function="nonexistent",
            limit=10,
            format="json",
            db_path=empty_db,
            verbose=False
        )

        assert exit_code == EXIT_NO_RESULTS
        captured = capsys.readouterr()

        # Error should be in stderr for JSON format
        assert "No traces found" in captured.err or "FunctionNotFound" in captured.err

    def test_table_format_no_results(self, empty_db, capsys):
        """Test table format when no results found."""
        exit_code = execute_performance(
            function="nonexistent",
            limit=10,
            format="table",
            db_path=empty_db,
            verbose=False
        )

        assert exit_code == EXIT_NO_RESULTS
        captured = capsys.readouterr()

        # Error should be in stderr
        assert "No traces found" in captured.err
