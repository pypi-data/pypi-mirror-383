"""
Tests for CLI list command.

Validates:
- List command execution
- Default limit (10 traces)
- Custom limit option
- JSON format output
- Table format output
- Empty database handling (EXIT_NO_RESULTS)
- Integration with CLI main
"""

import pytest
import tempfile
import os
import json
from datetime import datetime, timezone
import uuid

from typer.testing import CliRunner

from breadcrumb.cli.commands.list import execute_list, EXIT_SUCCESS, EXIT_ERROR, EXIT_NO_RESULTS
from breadcrumb.cli.main import app
from breadcrumb.storage.connection import reset_manager
from breadcrumb.storage.async_writer import TraceWriter


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
def empty_db(temp_db_path):
    """Create an empty database."""
    writer = TraceWriter(db_path=temp_db_path, batch_size=1)
    writer.start()
    import time
    time.sleep(0.1)
    writer.stop()
    return temp_db_path


@pytest.fixture
def populated_db(temp_db_path):
    """Create database with sample traces."""
    writer = TraceWriter(db_path=temp_db_path, batch_size=1)
    writer.start()

    # Add 15 sample traces to test limit functionality
    for i in range(15):
        trace_id = str(uuid.uuid4())
        writer.write_trace(
            trace_id=trace_id,
            started_at=datetime.now(timezone.utc),
            status='completed' if i % 2 == 0 else 'running',
            thread_id=12345 + i
        )

        writer.write_trace_event(
            event_id=str(uuid.uuid4()),
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc),
            event_type='call',
            function_name=f'test_func_{i}',
            module_name='__main__'
        )

    import time
    time.sleep(0.2)
    writer.stop()

    return temp_db_path


class TestListCommandDirect:
    """Test the execute_list function directly."""

    def test_list_default_limit(self, populated_db, capsys):
        """Test listing traces with default limit (10)."""
        exit_code = execute_list(
            limit=10,
            format="json",
            db_path=populated_db,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

        # Check output
        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert "traces" in output
        assert "count" in output
        assert output["count"] == 10  # Should return exactly 10
        assert len(output["traces"]) == 10

    def test_list_custom_limit(self, populated_db, capsys):
        """Test listing traces with custom limit."""
        exit_code = execute_list(
            limit=5,
            format="json",
            db_path=populated_db,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["count"] == 5
        assert len(output["traces"]) == 5

    def test_list_large_limit(self, populated_db, capsys):
        """Test listing with limit larger than available traces."""
        exit_code = execute_list(
            limit=100,
            format="json",
            db_path=populated_db,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        # Should return all 15 traces
        assert output["count"] == 15
        assert len(output["traces"]) == 15

    def test_list_json_format(self, populated_db, capsys):
        """Test JSON format output."""
        exit_code = execute_list(
            limit=3,
            format="json",
            db_path=populated_db,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        # Verify JSON structure
        assert isinstance(output, dict)
        assert "traces" in output
        assert isinstance(output["traces"], list)

        # Verify trace structure
        for trace in output["traces"]:
            assert "id" in trace
            assert "status" in trace
            assert "started_at" in trace

    def test_list_table_format(self, populated_db, capsys):
        """Test table format output."""
        exit_code = execute_list(
            limit=3,
            format="table",
            db_path=populated_db,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

        captured = capsys.readouterr()
        output = captured.out

        # Verify table format
        assert "Recent Traces" in output
        assert "|" in output  # Table separators
        assert "-" in output  # Header separator
        assert "Total: 3 rows" in output

    def test_list_empty_database_json(self, empty_db, capsys):
        """Test listing from empty database returns EXIT_NO_RESULTS (JSON)."""
        exit_code = execute_list(
            limit=10,
            format="json",
            db_path=empty_db,
            verbose=False
        )

        assert exit_code == EXIT_NO_RESULTS

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["count"] == 0
        assert output["traces"] == []
        assert "message" in output

    def test_list_empty_database_table(self, empty_db, capsys):
        """Test listing from empty database returns EXIT_NO_RESULTS (table)."""
        exit_code = execute_list(
            limit=10,
            format="table",
            db_path=empty_db,
            verbose=False
        )

        assert exit_code == EXIT_NO_RESULTS

        captured = capsys.readouterr()
        output = captured.out

        assert "No traces found" in output

    def test_list_verbose_mode(self, populated_db, capsys):
        """Test verbose mode outputs debug info."""
        exit_code = execute_list(
            limit=5,
            format="json",
            db_path=populated_db,
            verbose=True
        )

        assert exit_code == EXIT_SUCCESS

        captured = capsys.readouterr()
        # Verbose output goes to stderr
        assert "Querying" in captured.err or "traces" in captured.err.lower()

    def test_list_invalid_db_path(self, capsys):
        """Test with invalid database path creates empty db and returns EXIT_NO_RESULTS."""
        # Note: DuckDB will create the database at the path if it doesn't exist
        # So this test verifies that an empty database returns EXIT_NO_RESULTS
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db_path = os.path.join(tmpdir, "new.duckdb")

            exit_code = execute_list(
                limit=10,
                format="json",
                db_path=db_path,
                verbose=False
            )

            # New empty database should return EXIT_NO_RESULTS
            assert exit_code == EXIT_NO_RESULTS

            captured = capsys.readouterr()
            output = json.loads(captured.out)
            assert output["count"] == 0

            # Cleanup: close the connection before tempdir cleanup
            reset_manager()

    def test_list_ordered_by_started_at_desc(self, populated_db, capsys):
        """Test that traces are ordered by started_at DESC (most recent first)."""
        exit_code = execute_list(
            limit=15,
            format="json",
            db_path=populated_db,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        # Verify ordering
        traces = output["traces"]
        assert len(traces) == 15

        # Check that timestamps are in descending order
        for i in range(len(traces) - 1):
            current_time = traces[i]["started_at"]
            next_time = traces[i + 1]["started_at"]
            # Current should be >= next (more recent first)
            assert current_time >= next_time


class TestListCommandCLI:
    """Test the list command via CLI."""

    def test_list_command_default(self, populated_db):
        """Test 'breadcrumb list' with default settings."""
        result = runner.invoke(app, [
            "--db-path", populated_db,
            "--format", "json",
            "list"
        ])

        assert result.exit_code == EXIT_SUCCESS

        output = json.loads(result.stdout)
        assert output["count"] == 10  # Default limit
        assert len(output["traces"]) == 10

    def test_list_command_with_limit(self, populated_db):
        """Test 'breadcrumb list --limit 20'."""
        result = runner.invoke(app, [
            "--db-path", populated_db,
            "--format", "json",
            "list",
            "--limit", "20"
        ])

        assert result.exit_code == EXIT_SUCCESS

        output = json.loads(result.stdout)
        assert output["count"] == 15  # All available traces

    def test_list_command_table_format(self, populated_db):
        """Test 'breadcrumb list --format table'."""
        result = runner.invoke(app, [
            "--db-path", populated_db,
            "--format", "table",
            "list",
            "--limit", "5"
        ])

        assert result.exit_code == EXIT_SUCCESS
        assert "Recent Traces" in result.stdout
        assert "|" in result.stdout
        assert "Total: 5 rows" in result.stdout

    def test_list_command_empty_db(self, empty_db):
        """Test list command with empty database."""
        result = runner.invoke(app, [
            "--db-path", empty_db,
            "--format", "json",
            "list"
        ])

        assert result.exit_code == EXIT_NO_RESULTS

        output = json.loads(result.stdout)
        assert output["count"] == 0

    def test_list_command_short_option(self, populated_db):
        """Test 'breadcrumb list -n 7' (short option)."""
        result = runner.invoke(app, [
            "--db-path", populated_db,
            "-f", "json",
            "list",
            "-n", "7"
        ])

        assert result.exit_code == EXIT_SUCCESS

        output = json.loads(result.stdout)
        assert output["count"] == 7

    def test_list_command_verbose(self, populated_db):
        """Test list command with --verbose."""
        result = runner.invoke(app, [
            "--db-path", populated_db,
            "--verbose",
            "--format", "json",
            "list"
        ])

        assert result.exit_code == EXIT_SUCCESS
        # Verbose output in stderr
        assert "Breadcrumb CLI" in result.stderr or "Querying" in result.stderr

    def test_list_command_help(self):
        """Test 'breadcrumb list --help'."""
        result = runner.invoke(app, ["list", "--help"])

        assert result.exit_code == 0
        assert "list" in result.stdout.lower()
        assert "traces" in result.stdout.lower()
        assert "--limit" in result.stdout


class TestListOutputContent:
    """Test the content and structure of list command output."""

    def test_trace_fields_present(self, populated_db, capsys):
        """Test that all expected fields are present in trace output."""
        exit_code = execute_list(
            limit=1,
            format="json",
            db_path=populated_db,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        trace = output["traces"][0]

        # Verify required fields
        assert "id" in trace
        assert "status" in trace
        assert "started_at" in trace
        assert "ended_at" in trace
        assert "thread_id" in trace
        assert "metadata" in trace

    def test_trace_id_is_uuid(self, populated_db, capsys):
        """Test that trace IDs are valid UUIDs."""
        exit_code = execute_list(
            limit=3,
            format="json",
            db_path=populated_db,
            verbose=False
        )

        assert exit_code == EXIT_SUCCESS

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        for trace in output["traces"]:
            # Should be able to parse as UUID
            uuid.UUID(trace["id"])
