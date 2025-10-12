"""
Tests for query CLI command.

Validates:
- Successful query execution
- JSON output format
- Table output format
- Exit codes (success, error, no results)
- Error handling (invalid SQL, missing database)
"""

import pytest
import tempfile
import os
from datetime import datetime, timezone
import uuid
import json
from io import StringIO
from unittest.mock import patch

from breadcrumb.cli.commands.query import execute_query, EXIT_SUCCESS, EXIT_ERROR, EXIT_NO_RESULTS
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
    """Create database with sample data."""
    writer = TraceWriter(db_path=temp_db_path, batch_size=1)
    writer.start()

    # Add sample traces
    for i in range(5):
        trace_id = str(uuid.uuid4())
        writer.write_trace(
            trace_id=trace_id,
            started_at=datetime.now(timezone.utc),
            status='completed',
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


class TestQueryExecution:
    """Test query command execution."""

    def test_simple_query_json_format(self, populated_db):
        """Test simple query with JSON output."""
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            exit_code = execute_query(
                sql="SELECT * FROM traces LIMIT 5",
                format="json",
                db_path=populated_db,
                verbose=False
            )

            assert exit_code == EXIT_SUCCESS
            output = fake_stdout.getvalue()

            # Verify valid JSON
            data = json.loads(output)
            assert 'results' in data
            assert 'total' in data
            assert isinstance(data['results'], list)
            assert data['total'] > 0

    def test_simple_query_table_format(self, populated_db):
        """Test simple query with table output."""
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            exit_code = execute_query(
                sql="SELECT * FROM traces LIMIT 5",
                format="table",
                db_path=populated_db,
                verbose=False
            )

            assert exit_code == EXIT_SUCCESS
            output = fake_stdout.getvalue()

            # Verify table format
            assert '|' in output  # Table column separator
            assert '-' in output  # Table row separator
            assert 'Total:' in output  # Table footer

    def test_query_with_results(self, populated_db):
        """Test query that returns results."""
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            exit_code = execute_query(
                sql="SELECT id, status FROM traces WHERE status = 'completed'",
                format="json",
                db_path=populated_db,
                verbose=False
            )

            assert exit_code == EXIT_SUCCESS

            data = json.loads(fake_stdout.getvalue())
            assert data['total'] >= 1

            # Verify columns
            for row in data['results']:
                assert 'id' in row
                assert 'status' in row
                assert row['status'] == 'completed'

    def test_verbose_output(self, populated_db):
        """Test verbose mode."""
        with patch('sys.stdout', new=StringIO()):
            with patch('sys.stderr', new=StringIO()) as fake_stderr:
                exit_code = execute_query(
                    sql="SELECT * FROM traces LIMIT 1",
                    format="json",
                    db_path=populated_db,
                    verbose=True
                )

                assert exit_code == EXIT_SUCCESS

                stderr_output = fake_stderr.getvalue()
                assert 'Executing query' in stderr_output
                assert 'Query returned' in stderr_output


class TestNoResults:
    """Test handling of queries with no results."""

    def test_query_no_results_json(self, populated_db):
        """Test query with no results - JSON format."""
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            exit_code = execute_query(
                sql="SELECT * FROM traces WHERE status = 'nonexistent_status'",
                format="json",
                db_path=populated_db,
                verbose=False
            )

            assert exit_code == EXIT_NO_RESULTS

            # Verify valid JSON with empty results
            data = json.loads(fake_stdout.getvalue())
            assert data['results'] == []
            assert data['total'] == 0

    def test_query_no_results_table(self, populated_db):
        """Test query with no results - table format."""
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            exit_code = execute_query(
                sql="SELECT * FROM traces WHERE status = 'nonexistent_status'",
                format="table",
                db_path=populated_db,
                verbose=False
            )

            assert exit_code == EXIT_NO_RESULTS

            output = fake_stdout.getvalue()
            assert 'No results' in output


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_sql_query(self, populated_db):
        """Test invalid SQL query."""
        with patch('sys.stderr', new=StringIO()) as fake_stderr:
            exit_code = execute_query(
                sql="INSERT INTO traces VALUES (1, 2, 3)",
                format="json",
                db_path=populated_db,
                verbose=False
            )

            assert exit_code == EXIT_ERROR

            stderr_output = fake_stderr.getvalue()
            # Verify error is reported
            data = json.loads(stderr_output)
            assert 'error' in data
            assert data['error'] == 'InvalidQueryError'

    def test_sql_syntax_error(self, populated_db):
        """Test SQL syntax error."""
        with patch('sys.stderr', new=StringIO()) as fake_stderr:
            exit_code = execute_query(
                sql="SELECT * FROM nonexistent_table",
                format="json",
                db_path=populated_db,
                verbose=False
            )

            assert exit_code == EXIT_ERROR

            stderr_output = fake_stderr.getvalue()
            data = json.loads(stderr_output)
            assert 'error' in data

    def test_database_not_found(self):
        """Test missing database - DuckDB auto-creates, returns no results."""
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            exit_code = execute_query(
                sql="SELECT * FROM traces",
                format="json",
                db_path="/nonexistent/path/to/db.duckdb",
                verbose=False
            )

            # DuckDB auto-creates database if path is valid, returns no results
            assert exit_code == EXIT_NO_RESULTS

            stdout_output = fake_stdout.getvalue()
            data = json.loads(stdout_output)
            assert data['results'] == []
            assert data['total'] == 0

    def test_unsafe_query_rejected(self, populated_db):
        """Test that unsafe queries are rejected."""
        unsafe_queries = [
            "DELETE FROM traces",
            "UPDATE traces SET status = 'done'",
            "DROP TABLE traces",
            "CREATE TABLE foo (id INT)",
        ]

        for sql in unsafe_queries:
            with patch('sys.stderr', new=StringIO()) as fake_stderr:
                exit_code = execute_query(
                    sql=sql,
                    format="json",
                    db_path=populated_db,
                    verbose=False
                )

                assert exit_code == EXIT_ERROR, f"Query should be rejected: {sql}"

                stderr_output = fake_stderr.getvalue()
                data = json.loads(stderr_output)
                assert data['error'] == 'InvalidQueryError'


class TestOutputFormats:
    """Test different output formats."""

    def test_json_format_structure(self, populated_db):
        """Test JSON output structure."""
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            execute_query(
                sql="SELECT id, status FROM traces LIMIT 1",
                format="json",
                db_path=populated_db,
                verbose=False
            )

            data = json.loads(fake_stdout.getvalue())

            # Verify structure
            assert 'results' in data
            assert 'total' in data
            assert isinstance(data['results'], list)
            assert isinstance(data['total'], int)

    def test_table_format_structure(self, populated_db):
        """Test table output structure."""
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            execute_query(
                sql="SELECT id, status FROM traces LIMIT 3",
                format="table",
                db_path=populated_db,
                verbose=False
            )

            output = fake_stdout.getvalue()
            lines = output.split('\n')

            # Verify table structure
            # Should have: header, separator, rows, blank, footer
            assert len(lines) >= 5
            assert 'Total:' in output

    def test_error_format_json(self, populated_db):
        """Test error output in JSON format."""
        with patch('sys.stderr', new=StringIO()) as fake_stderr:
            execute_query(
                sql="DELETE FROM traces",
                format="json",
                db_path=populated_db,
                verbose=False
            )

            data = json.loads(fake_stderr.getvalue())

            assert 'error' in data
            assert 'message' in data
            assert 'suggestion' in data

    def test_error_format_table(self, populated_db):
        """Test error output in table format."""
        with patch('sys.stderr', new=StringIO()) as fake_stderr:
            execute_query(
                sql="DELETE FROM traces",
                format="table",
                db_path=populated_db,
                verbose=False
            )

            output = fake_stderr.getvalue()

            # Table format shows error as plain text
            assert 'ERROR:' in output or 'error' in output.lower()
            assert 'InvalidQueryError' in output


class TestIntegration:
    """Integration tests with CLI."""

    def test_query_count(self, populated_db):
        """Test COUNT query."""
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            exit_code = execute_query(
                sql="SELECT COUNT(*) as count FROM traces",
                format="json",
                db_path=populated_db,
                verbose=False
            )

            assert exit_code == EXIT_SUCCESS

            data = json.loads(fake_stdout.getvalue())
            assert len(data['results']) == 1
            assert 'count' in data['results'][0]

    def test_query_with_where_clause(self, populated_db):
        """Test query with WHERE clause."""
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            exit_code = execute_query(
                sql="SELECT * FROM trace_events WHERE event_type = 'call'",
                format="json",
                db_path=populated_db,
                verbose=False
            )

            assert exit_code == EXIT_SUCCESS

            data = json.loads(fake_stdout.getvalue())
            for row in data['results']:
                assert row['event_type'] == 'call'

    def test_query_with_join(self, populated_db):
        """Test query with JOIN."""
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            exit_code = execute_query(
                sql="""
                    SELECT t.id, t.status, COUNT(e.id) as event_count
                    FROM traces t
                    LEFT JOIN trace_events e ON t.id = e.trace_id
                    GROUP BY t.id, t.status
                """,
                format="json",
                db_path=populated_db,
                verbose=False
            )

            assert exit_code == EXIT_SUCCESS

            data = json.loads(fake_stdout.getvalue())
            assert len(data['results']) > 0
            for row in data['results']:
                assert 'id' in row
                assert 'status' in row
                assert 'event_count' in row
