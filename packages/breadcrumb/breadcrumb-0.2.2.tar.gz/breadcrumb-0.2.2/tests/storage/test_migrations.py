"""
Tests for schema migration system.

Validates:
- Schema version tracking
- Migration discovery and ordering
- Migration application
- Error handling
- Schema validation
"""

import pytest
import tempfile
import os
from pathlib import Path

from breadcrumb.storage.migrations import (
    MigrationManager,
    MigrationError,
    check_schema_version,
    apply_migrations,
    CURRENT_SCHEMA_VERSION,
)
from breadcrumb.storage.connection import get_manager, reset_manager


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


class TestMigrationManager:
    """Test MigrationManager class."""

    def test_initialization(self, temp_db_path):
        """Test manager initialization."""
        manager = MigrationManager(temp_db_path)

        assert manager.db_path == temp_db_path
        assert manager.migrations_dir.exists()

    def test_get_current_version_fresh_database(self, temp_db_path):
        """Test getting version from fresh database."""
        # Create fresh database
        conn_manager = get_manager(temp_db_path)
        conn_manager.get_connection()

        migration_manager = MigrationManager(temp_db_path)
        version = migration_manager.get_current_version()

        # Fresh database should report version 1 (from schema.sql)
        # because the schema is auto-applied by connection manager
        assert version == 1

    def test_get_current_version_with_migrations(self, temp_db_path):
        """Test getting version after migrations."""
        # Create database and apply initial schema
        conn_manager = get_manager(temp_db_path)
        conn_manager.get_connection()

        migration_manager = MigrationManager(temp_db_path)

        # Should be at version 1 (from initial schema)
        version = migration_manager.get_current_version()
        assert version == 1

    def test_needs_migration_fresh_database(self, temp_db_path):
        """Test needs_migration on fresh database."""
        # Create fresh database with schema v1
        conn_manager = get_manager(temp_db_path)
        conn_manager.get_connection()

        migration_manager = MigrationManager(temp_db_path)

        # Should not need migration (at current version)
        assert not migration_manager.needs_migration()

    def test_get_migration_history_empty(self, temp_db_path):
        """Test migration history on fresh database."""
        # Create database
        conn_manager = get_manager(temp_db_path)
        conn_manager.get_connection()

        migration_manager = MigrationManager(temp_db_path)
        history = migration_manager.get_migration_history()

        # Should have initial schema version
        assert len(history) >= 1
        assert history[0]['version'] == 1

    def test_validate_schema_current_version(self, temp_db_path):
        """Test schema validation when current."""
        # Create database at current version
        conn_manager = get_manager(temp_db_path)
        conn_manager.get_connection()

        migration_manager = MigrationManager(temp_db_path)

        # Should validate successfully
        assert migration_manager.validate_schema() is True

    def test_get_pending_migrations_returns_empty_list(self, temp_db_path):
        """Test pending migrations when up to date."""
        # Create database at current version
        conn_manager = get_manager(temp_db_path)
        conn_manager.get_connection()

        migration_manager = MigrationManager(temp_db_path)
        pending = migration_manager.get_pending_migrations()

        # Should have no pending migrations
        assert len(pending) == 0


class TestMigrationDiscovery:
    """Test migration file discovery."""

    def test_migration_files_exist(self):
        """Test that migration files exist."""
        migrations_dir = Path(__file__).parent.parent.parent / "src" / "breadcrumb" / "storage" / "migrations"

        # Should have at least v1_initial.sql
        v1_file = migrations_dir / "v1_initial.sql"
        assert v1_file.exists()


class TestMigrationApplication:
    """Test migration application."""

    def test_apply_migrations_no_pending(self, temp_db_path):
        """Test applying migrations when none pending."""
        # Create database at current version
        conn_manager = get_manager(temp_db_path)
        conn_manager.get_connection()

        migration_manager = MigrationManager(temp_db_path)
        applied = migration_manager.apply_migrations()

        # Should apply 0 migrations
        assert applied == 0


class TestHelperFunctions:
    """Test module-level helper functions."""

    def test_check_schema_version_current(self, temp_db_path):
        """Test schema version check when current."""
        # Create database at current version
        conn_manager = get_manager(temp_db_path)
        conn_manager.get_connection()

        # Should not raise
        try:
            check_schema_version(temp_db_path)
        except MigrationError:
            pytest.fail("Should not raise for current schema")

    def test_apply_migrations_helper(self, temp_db_path):
        """Test apply_migrations helper function."""
        # Create database
        conn_manager = get_manager(temp_db_path)
        conn_manager.get_connection()

        # Apply migrations
        applied = apply_migrations(temp_db_path)

        # Should apply 0 (already at current version)
        assert applied == 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_migration_manager_with_nonexistent_db(self, temp_db_path):
        """Test manager with non-existent database."""
        # Don't create database
        migration_manager = MigrationManager(temp_db_path)

        # get_current_version should handle gracefully
        # When connection manager creates database, it applies schema
        version = migration_manager.get_current_version()

        # Should be at version 1 (schema auto-applied)
        assert version == 1

    def test_current_schema_version_constant(self):
        """Test that CURRENT_SCHEMA_VERSION is defined."""
        assert CURRENT_SCHEMA_VERSION >= 1
        assert isinstance(CURRENT_SCHEMA_VERSION, int)
