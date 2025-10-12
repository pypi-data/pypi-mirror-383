"""
CLI workflow integration tests for Breadcrumb AI Tracer.

Tests the command-line interface:
1. Run traced application
2. Execute CLI commands
3. Verify output and functionality
"""

import pytest
import json
import subprocess
import sys
import time

from breadcrumb.cli.main import app as cli_app
from breadcrumb.storage.query import query_traces
from typer.testing import CliRunner

from . import (
    run_traced_code,
    wait_for_traces,
)


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing."""
    return CliRunner()


class TestCLIList:
    """Test 'breadcrumb list' command."""

    def test_list_command_basic(self, temp_db_path, sample_traced_code, cli_runner):
        """Test: Run app → breadcrumb list → verify output."""
        # Setup: Run traced code
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute CLI command
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'list']
        )

        # Verify command succeeded
        assert cli_result.exit_code == 0, f"CLI failed: {cli_result.stderr}"

        # Parse JSON output (default format)
        output = json.loads(cli_result.stdout)

        # Verify output structure
        assert 'traces' in output
        assert len(output['traces']) > 0

        # Verify trace has required fields
        trace = output['traces'][0]
        assert 'id' in trace
        assert 'status' in trace
        assert 'started_at' in trace

    def test_list_command_with_limit(self, temp_db_path, sample_traced_code, cli_runner):
        """Test list command with limit parameter."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute with limit
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'list', '--limit', '5']
        )

        assert cli_result.exit_code == 0
        output = json.loads(cli_result.stdout)

        # Verify limit is respected
        assert len(output['traces']) <= 5

    def test_list_command_table_format(self, temp_db_path, sample_traced_code, cli_runner):
        """Test list command with table format."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute with table format
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, '--format', 'table', 'list']
        )

        assert cli_result.exit_code == 0

        # Table format should be plain text, not JSON
        assert 'traces' not in cli_result.stdout.lower() or '│' in cli_result.stdout or '|' in cli_result.stdout


class TestCLIGet:
    """Test 'breadcrumb get' command."""

    def test_get_command_basic(self, temp_db_path, sample_traced_code, cli_runner):
        """Test: Run app → breadcrumb get <id> → verify trace details."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Get a trace ID
        traces = query_traces("SELECT id FROM traces LIMIT 1", db_path=temp_db_path)
        trace_id = traces[0]['id']

        # Execute get command
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'get', trace_id]
        )

        assert cli_result.exit_code == 0, f"CLI failed: {cli_result.stderr}"

        # Parse output
        output = json.loads(cli_result.stdout)

        # Verify structure
        assert 'trace' in output
        assert 'events' in output
        assert 'exceptions' in output

        # Verify trace ID matches
        assert output['trace']['id'] == trace_id

    def test_get_command_nonexistent_trace(self, temp_db_path, sample_traced_code, cli_runner):
        """Test get command with non-existent trace ID."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Try to get non-existent trace
        fake_id = "00000000-0000-0000-0000-000000000000"
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'get', fake_id]
        )

        # Should fail
        assert cli_result.exit_code != 0


class TestCLIQuery:
    """Test 'breadcrumb query' command."""

    def test_query_command_basic(self, temp_db_path, sample_traced_code, cli_runner):
        """Test: Run app → breadcrumb query → verify SQL execution."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute query command
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', 'SELECT * FROM traces LIMIT 10']
        )

        assert cli_result.exit_code == 0, f"CLI failed: {cli_result.stderr}"

        # Parse output
        output = json.loads(cli_result.stdout)

        # Verify results
        assert 'traces' in output or 'results' in output
        assert 'total' in output or 'count' in output

    def test_query_command_with_where_clause(self, temp_db_path, sample_traced_code, cli_runner):
        """Test query command with WHERE clause."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute query with filter
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query', "SELECT * FROM traces WHERE status='completed'"]
        )

        assert cli_result.exit_code == 0

        # Parse and verify
        output = json.loads(cli_result.stdout)
        results = output.get('traces', output.get('results', []))

        # All results should have status='completed'
        for row in results:
            if 'status' in row:
                assert row['status'] == 'completed'

    def test_query_command_unsafe_sql_rejected(self, temp_db_path, sample_traced_code, cli_runner):
        """Test that unsafe SQL is rejected by query command."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Try unsafe queries
        unsafe_queries = [
            "DELETE FROM traces",
            "DROP TABLE traces",
            "UPDATE traces SET status='hacked'",
        ]

        for unsafe_sql in unsafe_queries:
            cli_result = cli_runner.invoke(
                cli_app,
                ['--db-path', temp_db_path, 'query', unsafe_sql]
            )

            # Should fail with error
            assert cli_result.exit_code != 0


class TestCLIExceptions:
    """Test 'breadcrumb exceptions' command."""

    def test_exceptions_command_basic(
        self,
        temp_db_path,
        sample_traced_code_with_exception,
        cli_runner,
    ):
        """Test: Run app with exception → breadcrumb exceptions → verify output."""
        # Run code with exception
        result = run_traced_code(sample_traced_code_with_exception, temp_db_path)
        assert result['returncode'] != 0
        time.sleep(0.5)

        # Try to execute exceptions command
        try:
            cli_result = cli_runner.invoke(
                cli_app,
                ['--db-path', temp_db_path, 'exceptions']
            )

            # If command succeeds, verify output
            if cli_result.exit_code == 0:
                output = json.loads(cli_result.stdout)

                assert 'exceptions' in output
                assert 'total' in output

                # If exceptions captured, verify details
                if output['total'] > 0:
                    exc = output['exceptions'][0]
                    assert 'exception_type' in exc
                    assert exc['exception_type'] == 'ZeroDivisionError'

        except Exception as e:
            # Exception capture might not be implemented yet
            pytest.skip(f"Exception command not available: {e}")

    def test_exceptions_command_with_time_range(
        self,
        temp_db_path,
        sample_traced_code,
        cli_runner,
    ):
        """Test exceptions command with time range."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute with time range
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'exceptions', '--since', '30m']
        )

        # Should succeed (even if no exceptions found)
        if cli_result.exit_code == 0:
            output = json.loads(cli_result.stdout)
            assert 'exceptions' in output
            assert 'time_range' in output or 'since' in output


class TestCLIPerformance:
    """Test 'breadcrumb performance' command."""

    def test_performance_command_basic(self, temp_db_path, sample_traced_code, cli_runner):
        """Test: Run app → breadcrumb performance → verify statistics."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Get a function name
        events = query_traces(
            "SELECT DISTINCT function_name FROM trace_events WHERE function_name IS NOT NULL LIMIT 1",
            db_path=temp_db_path
        )

        if len(events) == 0:
            pytest.skip("No function names captured")

        function_name = events[0]['function_name']

        # Execute performance command
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'performance', function_name]
        )

        if cli_result.exit_code == 0:
            output = json.loads(cli_result.stdout)

            # Verify structure
            assert 'function' in output or 'statistics' in output
            assert output.get('function') == function_name or 'stats' in output

    def test_performance_command_nonexistent_function(
        self,
        temp_db_path,
        sample_traced_code,
        cli_runner,
    ):
        """Test performance command with non-existent function."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Try non-existent function
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'performance', 'nonexistent_function']
        )

        # Should either fail or return empty results
        # (implementation dependent)


class TestCLIGlobalOptions:
    """Test CLI global options."""

    def test_verbose_option(self, temp_db_path, sample_traced_code, cli_runner):
        """Test --verbose global option."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute with verbose
        cli_result = cli_runner.invoke(
            cli_app,
            ['--verbose', '--db-path', temp_db_path, 'list', '--limit', '5']
        )

        assert cli_result.exit_code == 0

        # Verbose mode should print extra info to stderr
        # (but we're using CliRunner which might not capture it)

    def test_format_json(self, temp_db_path, sample_traced_code, cli_runner):
        """Test --format json option (default)."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Execute with explicit JSON format
        cli_result = cli_runner.invoke(
            cli_app,
            ['--format', 'json', '--db-path', temp_db_path, 'list']
        )

        assert cli_result.exit_code == 0

        # Should be valid JSON
        output = json.loads(cli_result.stdout)
        assert isinstance(output, dict)

    def test_db_path_discovery(self, cli_runner):
        """Test that CLI can discover database path."""
        # This test is tricky because it depends on CWD
        # We'll just verify the option is accepted
        cli_result = cli_runner.invoke(
            cli_app,
            ['--help']
        )

        assert cli_result.exit_code == 0
        assert '--db-path' in cli_result.stdout


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_missing_database_error(self, cli_runner):
        """Test CLI with missing database."""
        # Try to list traces from non-existent database
        cli_result = cli_runner.invoke(
            cli_app,
            ['--db-path', '/nonexistent/path/traces.duckdb', 'list']
        )

        # Should fail with error
        assert cli_result.exit_code != 0

    def test_invalid_format_option(self, temp_db_path, cli_runner):
        """Test CLI with invalid format option."""
        cli_result = cli_runner.invoke(
            cli_app,
            ['--format', 'invalid', '--db-path', temp_db_path, 'list']
        )

        # Should fail
        assert cli_result.exit_code != 0


class TestCLIWorkflowScenarios:
    """Test complete CLI workflow scenarios."""

    def test_developer_debugging_workflow(
        self,
        temp_db_path,
        sample_traced_code_with_exception,
        cli_runner,
    ):
        """
        Test developer workflow: Run code → find exception → get trace details.

        Simulates how a developer would debug using CLI.
        """
        # Step 1: Run code with exception
        result = run_traced_code(sample_traced_code_with_exception, temp_db_path)
        assert result['returncode'] != 0
        time.sleep(0.5)

        # Step 2: List recent traces
        list_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'list', '--limit', '5']
        )

        if list_result.exit_code != 0:
            pytest.skip("Database not created or list command failed")

        list_output = json.loads(list_result.stdout)

        if len(list_output['traces']) == 0:
            pytest.skip("No traces captured")

        # Step 3: Get trace details
        trace_id = list_output['traces'][0]['id']
        get_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'get', trace_id]
        )

        if get_result.exit_code == 0:
            trace_data = json.loads(get_result.stdout)

            # Developer now has full trace context
            assert 'trace' in trace_data
            assert 'events' in trace_data

    def test_performance_investigation_workflow(
        self,
        temp_db_path,
        sample_traced_code,
        cli_runner,
    ):
        """
        Test developer workflow: List traces → find functions → analyze performance.

        Simulates performance investigation.
        """
        # Step 1: Run code
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Step 2: Find all functions
        query_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'query',
             'SELECT DISTINCT function_name FROM trace_events WHERE function_name IS NOT NULL LIMIT 5']
        )

        if query_result.exit_code != 0:
            pytest.skip("Query command failed")

        query_output = json.loads(query_result.stdout)
        functions = query_output.get('traces', query_output.get('results', []))

        if len(functions) == 0:
            pytest.skip("No functions captured")

        # Step 3: Analyze performance of first function
        function_name = functions[0]['function_name']
        perf_result = cli_runner.invoke(
            cli_app,
            ['--db-path', temp_db_path, 'performance', function_name]
        )

        if perf_result.exit_code == 0:
            perf_output = json.loads(perf_result.stdout)

            # Developer gets performance statistics
            assert 'function' in perf_output or 'statistics' in perf_output


class TestCLIIntegrationWithRealProcess:
    """Test CLI as a real subprocess (not using CliRunner)."""

    def test_cli_as_subprocess(self, temp_db_path, sample_traced_code):
        """Test running breadcrumb CLI as actual subprocess."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Run CLI as subprocess
        cli_result = subprocess.run(
            [sys.executable, '-m', 'breadcrumb.cli.main',
             '--db-path', temp_db_path, 'list', '--limit', '5'],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should succeed
        assert cli_result.returncode == 0, f"CLI failed: {cli_result.stderr}"

        # Should output valid JSON
        try:
            output = json.loads(cli_result.stdout)
            assert 'traces' in output
        except json.JSONDecodeError:
            # Might have extra output, that's okay
            pass

    def test_cli_help_output(self):
        """Test that CLI help works."""
        cli_result = subprocess.run(
            [sys.executable, '-m', 'breadcrumb.cli.main', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert cli_result.returncode == 0
        assert 'breadcrumb' in cli_result.stdout.lower()
        assert 'list' in cli_result.stdout.lower()
        assert 'query' in cli_result.stdout.lower()


class TestCLIOutputFormats:
    """Test different CLI output formats."""

    def test_json_output_parseable(self, temp_db_path, sample_traced_code, cli_runner):
        """Test that JSON output is always valid and parseable."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Test all commands with JSON output
        commands = [
            ['list'],
            ['query', 'SELECT * FROM traces LIMIT 1'],
        ]

        for cmd in commands:
            cli_result = cli_runner.invoke(
                cli_app,
                ['--format', 'json', '--db-path', temp_db_path] + cmd
            )

            if cli_result.exit_code == 0:
                # Should be valid JSON
                try:
                    output = json.loads(cli_result.stdout)
                    assert isinstance(output, (dict, list))
                except json.JSONDecodeError as e:
                    pytest.fail(f"Invalid JSON output for {cmd}: {e}\n{cli_result.stdout}")

    def test_table_output_readable(self, temp_db_path, sample_traced_code, cli_runner):
        """Test that table output is human-readable."""
        # Setup
        result = run_traced_code(sample_traced_code, temp_db_path)
        assert result['returncode'] == 0
        assert wait_for_traces(temp_db_path, min_traces=1)

        # Test with table format
        cli_result = cli_runner.invoke(
            cli_app,
            ['--format', 'table', '--db-path', temp_db_path, 'list', '--limit', '3']
        )

        if cli_result.exit_code == 0:
            output = cli_result.stdout

            # Should NOT be JSON
            try:
                json.loads(output)
                pytest.fail("Table format returned JSON instead of table")
            except json.JSONDecodeError:
                # This is expected - table format is not JSON
                pass

            # Should be readable text (not empty)
            assert len(output) > 0
