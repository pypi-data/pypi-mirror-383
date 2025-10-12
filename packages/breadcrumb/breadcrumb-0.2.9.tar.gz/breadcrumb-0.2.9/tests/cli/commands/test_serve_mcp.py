"""
Tests for CLI command: serve-mcp

Validates that the serve-mcp command correctly starts the MCP server,
handles database paths, and provides proper error messages.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from breadcrumb.cli.main import app, EXIT_SUCCESS, EXIT_ERROR
from breadcrumb.storage.connection import get_manager, reset_manager


runner = CliRunner()


@pytest.fixture
def temp_workspace():
    """Create temporary workspace with .breadcrumb directory and database."""
    # Reset singleton to avoid interference from previous tests
    reset_manager()

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        workspace = Path(tmpdir)
        breadcrumb_dir = workspace / ".breadcrumb"
        breadcrumb_dir.mkdir(parents=True)

        # Create database with fresh manager
        db_path = breadcrumb_dir / "traces.duckdb"
        manager = get_manager(str(db_path))
        conn = manager.get_connection()  # Initialize database
        conn.execute("SELECT 1")  # Ensure database is created
        conn.commit()  # Flush to disk

        yield workspace, db_path

        # Cleanup after test
        reset_manager()


class TestServeMcpCommand:
    """Test serve-mcp command execution."""

    def test_serve_mcp_command_help(self):
        """Test serve-mcp command help message."""
        result = runner.invoke(app, ["serve-mcp", "--help"])

        assert result.exit_code == 0
        assert "mcp" in result.stdout.lower()
        assert "server" in result.stdout.lower()
        assert "--db-path" in result.stdout

    @patch('breadcrumb.cli.commands.serve_mcp.run_server')
    def test_serve_mcp_starts_server(self, mock_run_server, temp_workspace):
        """Test that serve-mcp starts the MCP server."""
        workspace, db_path = temp_workspace

        # Mock run_server to avoid blocking
        mock_run_server.return_value = None

        result = runner.invoke(app, ["serve-mcp", "--db-path", str(db_path)])

        # Verify run_server was called with correct db_path
        mock_run_server.assert_called_once_with(str(db_path))
        assert result.exit_code == EXIT_SUCCESS

    @patch('breadcrumb.cli.commands.serve_mcp.run_server')
    def test_serve_mcp_auto_discovers_database(self, mock_run_server, temp_workspace, monkeypatch):
        """Test that serve-mcp auto-discovers database when path not provided."""
        workspace, db_path = temp_workspace

        # Change to workspace directory so auto-discovery works
        monkeypatch.chdir(workspace)

        # Mock run_server to avoid blocking
        mock_run_server.return_value = None

        result = runner.invoke(app, ["serve-mcp"])

        # Verify run_server was called (with None for auto-discovery)
        mock_run_server.assert_called_once_with(None)
        assert result.exit_code == EXIT_SUCCESS

    @patch('breadcrumb.cli.commands.serve_mcp.run_server')
    def test_serve_mcp_with_verbose_flag(self, mock_run_server, temp_workspace):
        """Test serve-mcp with verbose flag shows startup messages."""
        workspace, db_path = temp_workspace

        # Mock run_server to avoid blocking
        mock_run_server.return_value = None

        result = runner.invoke(app, ["--verbose", "serve-mcp", "--db-path", str(db_path)])

        # Verify verbose output
        assert "Starting Breadcrumb MCP Server" in result.stderr
        assert str(db_path) in result.stderr
        assert result.exit_code == EXIT_SUCCESS

    @patch('breadcrumb.cli.commands.serve_mcp.run_server')
    def test_serve_mcp_handles_keyboard_interrupt(self, mock_run_server, temp_workspace):
        """Test that serve-mcp handles Ctrl+C gracefully."""
        workspace, db_path = temp_workspace

        # Mock run_server to raise KeyboardInterrupt
        mock_run_server.side_effect = KeyboardInterrupt()

        result = runner.invoke(app, ["serve-mcp", "--db-path", str(db_path)])

        # Should exit successfully on Ctrl+C
        assert result.exit_code == EXIT_SUCCESS

    @patch('breadcrumb.cli.commands.serve_mcp.run_server')
    def test_serve_mcp_handles_keyboard_interrupt_verbose(self, mock_run_server, temp_workspace):
        """Test that serve-mcp shows shutdown message with verbose flag."""
        workspace, db_path = temp_workspace

        # Mock run_server to raise KeyboardInterrupt
        mock_run_server.side_effect = KeyboardInterrupt()

        result = runner.invoke(app, ["--verbose", "serve-mcp", "--db-path", str(db_path)])

        # Should show shutdown message
        assert "Server shutdown complete" in result.stderr
        assert result.exit_code == EXIT_SUCCESS

    @patch('breadcrumb.cli.commands.serve_mcp.run_server')
    def test_serve_mcp_handles_system_exit(self, mock_run_server, temp_workspace):
        """Test that serve-mcp handles SystemExit from run_server."""
        workspace, db_path = temp_workspace

        # Mock run_server to raise SystemExit (what run_server does on error)
        mock_run_server.side_effect = SystemExit(1)

        result = runner.invoke(app, ["serve-mcp", "--db-path", str(db_path)])

        # Should propagate exit code
        assert result.exit_code == EXIT_ERROR

    @patch('breadcrumb.cli.commands.serve_mcp.run_server')
    def test_serve_mcp_handles_unexpected_error(self, mock_run_server, temp_workspace):
        """Test that serve-mcp handles unexpected errors."""
        workspace, db_path = temp_workspace

        # Mock run_server to raise unexpected error
        mock_run_server.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(app, ["serve-mcp", "--db-path", str(db_path)])

        # Should exit with error
        assert result.exit_code == EXIT_ERROR
        assert "Error:" in result.stderr or "error" in result.stderr.lower()

    @patch('breadcrumb.cli.commands.serve_mcp.run_server')
    def test_serve_mcp_port_option_shows_warning(self, mock_run_server, temp_workspace):
        """Test that --port option shows warning (TCP not implemented)."""
        workspace, db_path = temp_workspace

        # Mock run_server to avoid blocking
        mock_run_server.return_value = None

        result = runner.invoke(app, ["serve-mcp", "--db-path", str(db_path), "--port", "8080"])

        # Should show warning about TCP not implemented
        assert "TCP transport not yet implemented" in result.stderr or "Warning" in result.stderr
        # Should still start server with stdio
        mock_run_server.assert_called_once()
        assert result.exit_code == EXIT_SUCCESS

    @patch('breadcrumb.cli.commands.serve_mcp.run_server')
    def test_serve_mcp_respects_global_db_path(self, mock_run_server, temp_workspace):
        """Test that serve-mcp respects global --db-path option."""
        workspace, db_path = temp_workspace

        # Mock run_server to avoid blocking
        mock_run_server.return_value = None

        result = runner.invoke(app, ["--db-path", str(db_path), "serve-mcp"])

        # Verify run_server was called with global db_path
        mock_run_server.assert_called_once_with(str(db_path))
        assert result.exit_code == EXIT_SUCCESS

    @patch('breadcrumb.cli.commands.serve_mcp.run_server')
    def test_serve_mcp_command_overrides_global_db_path(self, mock_run_server, temp_workspace):
        """Test that command-specific --db-path overrides global."""
        workspace, db_path = temp_workspace
        other_path = workspace / "other.duckdb"

        # Mock run_server to avoid blocking
        mock_run_server.return_value = None

        result = runner.invoke(
            app,
            ["--db-path", str(other_path), "serve-mcp", "--db-path", str(db_path)]
        )

        # Command-specific path should override global
        mock_run_server.assert_called_once_with(str(db_path))
        assert result.exit_code == EXIT_SUCCESS


class TestServeMcpIntegration:
    """Integration tests for serve-mcp command with actual MCP server."""

    @patch('breadcrumb.mcp.server.create_mcp_server')
    def test_serve_mcp_creates_server_with_correct_path(self, mock_create_server, temp_workspace):
        """Test that serve-mcp creates MCP server with correct database path."""
        workspace, db_path = temp_workspace

        # Mock the MCP server creation
        mock_server = MagicMock()
        mock_create_server.return_value = mock_server
        mock_server.run.return_value = None

        # Patch run_server to call create_mcp_server but not actually run
        with patch('breadcrumb.cli.commands.serve_mcp.run_server') as mock_run:
            # Make run_server call create_mcp_server
            def side_effect(db_path):
                from breadcrumb.mcp.server import create_mcp_server
                create_mcp_server(db_path)

            mock_run.side_effect = side_effect

            result = runner.invoke(app, ["serve-mcp", "--db-path", str(db_path)])

            # Verify create_mcp_server was called with correct path
            mock_create_server.assert_called_once_with(str(db_path))

    @patch('breadcrumb.cli.commands.serve_mcp.run_server')
    def test_serve_mcp_with_missing_database_shows_error(self, mock_run_server):
        """Test that serve-mcp shows helpful error when database not found."""
        # Use invalid path
        invalid_path = "/nonexistent/path/traces.duckdb"

        # Mock run_server to raise SystemExit(1) as it does on error
        mock_run_server.side_effect = SystemExit(1)

        result = runner.invoke(app, ["serve-mcp", "--db-path", invalid_path])

        # Should exit with error
        assert result.exit_code == EXIT_ERROR
        # Error message handled by run_server
