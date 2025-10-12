"""
Schema migrations for Breadcrumb storage layer.
"""

from breadcrumb.storage.migrations.migration_manager import (
    MigrationManager,
    MigrationError,
    check_schema_version,
    apply_migrations,
    CURRENT_SCHEMA_VERSION,
)

__all__ = [
    'MigrationManager',
    'MigrationError',
    'check_schema_version',
    'apply_migrations',
    'CURRENT_SCHEMA_VERSION',
]
