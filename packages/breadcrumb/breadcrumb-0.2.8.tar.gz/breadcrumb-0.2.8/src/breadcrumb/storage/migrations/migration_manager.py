"""
Schema migration manager for version upgrades.

Handles schema version tracking and applying pending migrations safely.
"""

import os
from typing import List, Tuple, Optional
from pathlib import Path
import re

from breadcrumb.storage.connection import get_manager


# Current schema version
CURRENT_SCHEMA_VERSION = 1


class MigrationError(Exception):
    """Raised when migration fails."""
    pass


class MigrationManager:
    """
    Manages schema versioning and migrations.

    Features:
    - Tracks current schema version in database
    - Discovers pending migrations from filesystem
    - Applies migrations in order with transaction safety
    - Validates migration integrity

    Example:
        manager = MigrationManager()
        if manager.needs_migration():
            manager.apply_migrations()
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize migration manager.

        Args:
            db_path: Optional database path
        """
        self.db_path = db_path
        self.migrations_dir = Path(__file__).parent

    def get_current_version(self) -> int:
        """
        Get current schema version from database.

        Returns:
            Current version number (0 if no schema exists)

        Raises:
            MigrationError: If version table check fails
        """
        manager = get_manager(self.db_path)

        try:
            # Check if version table exists
            result = manager.execute_with_retry("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name = '_breadcrumb_schema_version'
            """)

            if result.fetchone()[0] == 0:
                # No version table = fresh database
                return 0

            # Get current version
            version_result = manager.execute_with_retry("""
                SELECT version FROM _breadcrumb_schema_version
                ORDER BY applied_at DESC
                LIMIT 1
            """)

            row = version_result.fetchone()
            if row is None:
                return 0

            return row[0]

        except Exception as e:
            raise MigrationError(f"Failed to get current schema version: {e}")

    def needs_migration(self) -> bool:
        """
        Check if database needs migration.

        Returns:
            True if database schema is outdated
        """
        current_version = self.get_current_version()
        return current_version < CURRENT_SCHEMA_VERSION

    def get_pending_migrations(self) -> List[Tuple[int, Path]]:
        """
        Discover pending migration files.

        Returns:
            List of (version, file_path) tuples sorted by version

        Raises:
            MigrationError: If migration files are invalid
        """
        current_version = self.get_current_version()
        pending = []

        # Pattern: v{version}_{description}.sql
        pattern = re.compile(r'^v(\d+)_.*\.sql$')

        for file_path in self.migrations_dir.glob('v*.sql'):
            match = pattern.match(file_path.name)
            if not match:
                continue

            version = int(match.group(1))

            if version > current_version:
                pending.append((version, file_path))

        # Sort by version
        pending.sort(key=lambda x: x[0])

        # Validate sequential versions
        for i, (version, _) in enumerate(pending):
            expected_version = current_version + i + 1
            if version != expected_version:
                raise MigrationError(
                    f"Missing migration v{expected_version}. "
                    f"Found v{version} instead. Migrations must be sequential."
                )

        return pending

    def apply_migrations(self) -> int:
        """
        Apply all pending migrations.

        Returns:
            Number of migrations applied

        Raises:
            MigrationError: If migration fails
        """
        pending = self.get_pending_migrations()

        if not pending:
            return 0

        manager = get_manager(self.db_path)
        applied_count = 0

        for version, migration_file in pending:
            try:
                # Read migration SQL
                with open(migration_file, 'r', encoding='utf-8') as f:
                    migration_sql = f.read()

                # Apply migration in transaction
                with manager.get_connection_context() as conn:
                    # Execute migration SQL
                    conn.execute(migration_sql)

                    # Record migration
                    conn.execute("""
                        INSERT INTO _breadcrumb_schema_version (version, description, applied_at)
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                    """, [version, migration_file.stem])

                applied_count += 1

                print(f"Applied migration: {migration_file.name}")

            except Exception as e:
                raise MigrationError(
                    f"Failed to apply migration {migration_file.name}: {e}"
                )

        return applied_count

    def get_migration_history(self) -> List[dict]:
        """
        Get migration history from database.

        Returns:
            List of migration records with version, description, applied_at
        """
        manager = get_manager(self.db_path)

        try:
            result = manager.execute_with_retry("""
                SELECT version, description, applied_at
                FROM _breadcrumb_schema_version
                ORDER BY version
            """)

            rows = result.fetchall()
            if not rows:
                return []

            columns = [desc[0] for desc in result.description]
            return [dict(zip(columns, row)) for row in rows]

        except Exception:
            # Table doesn't exist yet
            return []

    def validate_schema(self) -> bool:
        """
        Validate that current schema matches expected version.

        Returns:
            True if schema is valid and current

        Raises:
            MigrationError: If schema is invalid or needs migration
        """
        current_version = self.get_current_version()

        if current_version < CURRENT_SCHEMA_VERSION:
            raise MigrationError(
                f"Database schema is outdated (v{current_version}). "
                f"Current version is v{CURRENT_SCHEMA_VERSION}. "
                f"Run 'breadcrumb migrate' to apply pending migrations."
            )

        if current_version > CURRENT_SCHEMA_VERSION:
            raise MigrationError(
                f"Database schema is newer (v{current_version}) than this version "
                f"of Breadcrumb (v{CURRENT_SCHEMA_VERSION}). "
                f"Please upgrade Breadcrumb."
            )

        return True


def check_schema_version(db_path: Optional[str] = None) -> None:
    """
    Check schema version and warn if migration needed.

    Args:
        db_path: Optional database path

    Raises:
        MigrationError: If schema needs migration
    """
    manager = MigrationManager(db_path)

    if manager.needs_migration():
        current = manager.get_current_version()
        pending = len(manager.get_pending_migrations())

        raise MigrationError(
            f"Database schema is outdated (v{current}). "
            f"{pending} pending migration(s). "
            f"Run 'breadcrumb migrate' to upgrade."
        )


def apply_migrations(db_path: Optional[str] = None) -> int:
    """
    Apply all pending migrations.

    Args:
        db_path: Optional database path

    Returns:
        Number of migrations applied

    Raises:
        MigrationError: If migration fails
    """
    manager = MigrationManager(db_path)
    return manager.apply_migrations()
