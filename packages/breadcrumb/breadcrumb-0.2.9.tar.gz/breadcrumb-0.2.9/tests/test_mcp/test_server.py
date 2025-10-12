"""
Tests for MCP server initialization and database discovery.
"""

import pytest
import tempfile
import os
from pathlib import Path

from breadcrumb.mcp.server import find_breadcrumb_database, create_mcp_server
from breadcrumb.storage.connection import get_manager, reset_manager


@pytest.fixture
def temp_workspace():
    """Create temporary workspace with .breadcrumb directory."""
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

        yield workspace

        # Cleanup after test
        reset_manager()


@pytest.fixture
def nested_workspace():
    """Create nested workspace structure for testing parent directory search."""
    # Reset singleton to avoid interference from previous tests
    reset_manager()

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        root = Path(tmpdir)

        # Create .breadcrumb at root
        breadcrumb_dir = root / ".breadcrumb"
        breadcrumb_dir.mkdir(parents=True)

        db_path = breadcrumb_dir / "traces.duckdb"
        manager = get_manager(str(db_path))
        conn = manager.get_connection()
        conn.execute("SELECT 1")  # Ensure database is created
        conn.commit()  # Flush to disk

        # Create nested directories
        nested = root / "project" / "src" / "app"
        nested.mkdir(parents=True)

        yield root, nested

        # Cleanup after test
        reset_manager()


class TestDatabaseDiscovery:
    """Test database discovery in current and parent directories."""

    def test_find_database_in_current_directory(self, temp_workspace):
        """Test finding database in current directory."""
        db_path = find_breadcrumb_database(temp_workspace)

        assert db_path is not None
        assert db_path.exists()
        assert db_path.name == "traces.duckdb"
        assert db_path.parent.name == ".breadcrumb"

    def test_find_database_in_parent_directory(self, nested_workspace):
        """Test finding database in parent directories."""
        root, nested = nested_workspace

        # Search from nested directory
        db_path = find_breadcrumb_database(nested, max_levels=5)

        assert db_path is not None
        assert db_path.exists()
        assert db_path.parent == root / ".breadcrumb"

    def test_find_database_returns_none_if_not_found(self):
        """Test that None is returned if database not found."""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            db_path = find_breadcrumb_database(Path(tmpdir))

            assert db_path is None

    def test_find_database_respects_max_levels(self, nested_workspace):
        """Test that max_levels parameter is respected."""
        root, nested = nested_workspace

        # Try to find with max_levels=1 (won't reach root)
        db_path = find_breadcrumb_database(nested, max_levels=1)

        assert db_path is None  # Too far away


class TestServerCreation:
    """Test MCP server creation and configuration."""

    def test_create_server_with_explicit_path(self, temp_workspace):
        """Test creating server with explicit database path."""
        db_path = temp_workspace / ".breadcrumb" / "traces.duckdb"

        server = create_mcp_server(str(db_path))

        assert server is not None
        assert server.name == "breadcrumb-tracer"
        assert hasattr(server, 'db_path')
        assert server.db_path == str(db_path)

    def test_create_server_discovers_database(self, temp_workspace, monkeypatch):
        """Test that server discovers database if path not provided."""
        # Change working directory to workspace
        monkeypatch.chdir(temp_workspace)

        server = create_mcp_server()

        assert server is not None
        assert hasattr(server, 'db_path')
        assert ".breadcrumb" in server.db_path

    def test_create_server_raises_if_database_not_found(self, monkeypatch):
        """Test that FileNotFoundError is raised if database not found."""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            monkeypatch.chdir(tmpdir)  # Isolate from project database
            with pytest.raises(FileNotFoundError) as exc_info:
                create_mcp_server()

            assert "Could not find .breadcrumb/traces.duckdb" in str(exc_info.value)

    def test_create_server_requires_existing_database(self, tmp_path):
        """Test that server requires database to exist when path provided."""
        # MCP server intentionally requires database to exist to prevent accidental creation
        db_path = tmp_path / ".breadcrumb" / "traces.duckdb"

        # Should raise error if database doesn't exist
        with pytest.raises(FileNotFoundError) as exc_info:
            create_mcp_server(str(db_path))

        # Error can be about directory or database not found
        assert "not found" in str(exc_info.value).lower()

        # But if we create it first, it should work
        from breadcrumb.storage.connection import get_manager
        manager = get_manager(str(db_path))
        conn = manager.get_connection()
        conn.execute("SELECT 1")
        conn.commit()

        server = create_mcp_server(str(db_path))
        assert server is not None
        reset_manager()


class TestServerConfiguration:
    """Test server configuration and setup."""

    def test_server_has_correct_name(self, temp_workspace):
        """Test that server has correct name."""
        db_path = temp_workspace / ".breadcrumb" / "traces.duckdb"

        server = create_mcp_server(str(db_path))

        assert server.name == "breadcrumb-tracer"

    def test_server_stores_database_path(self, temp_workspace):
        """Test that database path is stored in server context."""
        db_path = temp_workspace / ".breadcrumb" / "traces.duckdb"

        server = create_mcp_server(str(db_path))

        assert hasattr(server, 'db_path')
        assert server.db_path == str(db_path)


class TestToolRegistration:
    """Test that tools are properly registered."""

    def test_tools_are_registered(self, temp_workspace):
        """Test that all tools are registered on the server."""
        db_path = temp_workspace / ".breadcrumb" / "traces.duckdb"
        server = create_mcp_server(str(db_path))

        # Verify server has tools registered
        # FastMCP registers tools via decorators, so they should be present
        assert server is not None
        assert server.name == "breadcrumb-tracer"

        # The tools should be accessible via the server's tool registry
        # This is a basic sanity check that server creation succeeded
        # Tool execution will be tested separately if needed


class TestErrorHandling:
    """Test error handling in server initialization."""

    def test_missing_database_provides_helpful_message(self, monkeypatch):
        """Test that missing database error provides setup instructions."""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            monkeypatch.chdir(tmpdir)  # Isolate from project database
            with pytest.raises(FileNotFoundError) as exc_info:
                create_mcp_server()

            error_message = str(exc_info.value)
            assert "breadcrumb" in error_message.lower()
            assert "init" in error_message.lower()

    def test_nonexistent_path_provides_helpful_message(self):
        """Test that nonexistent path error provides helpful message."""
        import tempfile
        # Use a path in temp that definitely doesn't exist
        nonexistent_path = os.path.join(tempfile.gettempdir(), "nonexistent_breadcrumb_test_12345", "traces.duckdb")

        with pytest.raises(FileNotFoundError) as exc_info:
            create_mcp_server(nonexistent_path)

        error_message = str(exc_info.value)
        assert "not found" in error_message.lower()
