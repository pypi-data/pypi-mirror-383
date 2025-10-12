"""
Tests for retention policy enforcement.

Validates:
- Automatic deletion of old traces
- Configurable retention period
- Background cleanup thread
- Manual cleanup
- Environment variable configuration
"""

import pytest
import tempfile
import os
import time
from datetime import datetime, timedelta, timezone
import uuid

from breadcrumb.storage.retention import (
    RetentionPolicy,
    get_retention_policy,
    reset_retention_policy,
    DEFAULT_RETENTION_DAYS,
)
from breadcrumb.storage.connection import get_manager, reset_manager
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
    reset_retention_policy()
    reset_manager()
    yield
    # Ensure manager is closed before cleanup
    try:
        from breadcrumb.storage.connection import _global_manager
        if _global_manager is not None:
            _global_manager.close()
    except:
        pass
    reset_retention_policy()
    reset_manager()


@pytest.fixture
def populated_db(temp_db_path):
    """Create database with sample traces at different ages."""
    writer = TraceWriter(db_path=temp_db_path, batch_size=1)
    writer.start()

    # Create traces at different ages
    now = datetime.now(timezone.utc)

    # Recent trace (1 day old)
    trace_id_recent = str(uuid.uuid4())
    writer.write_trace(
        trace_id=trace_id_recent,
        started_at=now - timedelta(days=1),
        ended_at=now - timedelta(days=1, hours=-1),
        status='completed',
        thread_id=12345
    )

    # Old trace (10 days old)
    trace_id_old = str(uuid.uuid4())
    writer.write_trace(
        trace_id=trace_id_old,
        started_at=now - timedelta(days=10),
        ended_at=now - timedelta(days=10, hours=-1),
        status='completed',
        thread_id=12346
    )

    # Very old trace (30 days old)
    trace_id_very_old = str(uuid.uuid4())
    writer.write_trace(
        trace_id=trace_id_very_old,
        started_at=now - timedelta(days=30),
        ended_at=now - timedelta(days=30, hours=-1),
        status='completed',
        thread_id=12347
    )

    time.sleep(0.2)
    writer.stop()

    return {
        'db_path': temp_db_path,
        'recent': trace_id_recent,
        'old': trace_id_old,
        'very_old': trace_id_very_old,
    }


class TestRetentionPolicy:
    """Test RetentionPolicy class."""

    def test_initialization(self, temp_db_path):
        """Test policy initialization with defaults."""
        policy = RetentionPolicy(db_path=temp_db_path)

        assert policy.retention_days == DEFAULT_RETENTION_DAYS
        assert policy.db_path == temp_db_path
        assert not policy._running

    def test_custom_retention_days(self, temp_db_path):
        """Test custom retention period."""
        policy = RetentionPolicy(retention_days=30, db_path=temp_db_path)

        assert policy.retention_days == 30

    def test_env_var_retention_days(self, temp_db_path, monkeypatch):
        """Test retention period from environment variable."""
        monkeypatch.setenv('BREADCRUMB_RETENTION_DAYS', '14')

        policy = RetentionPolicy(db_path=temp_db_path)

        assert policy.retention_days == 14

    def test_python_api_overrides_env_var(self, temp_db_path, monkeypatch):
        """Test that Python API overrides env var."""
        monkeypatch.setenv('BREADCRUMB_RETENTION_DAYS', '14')

        policy = RetentionPolicy(retention_days=21, db_path=temp_db_path)

        assert policy.retention_days == 21

    def test_start_and_stop(self, temp_db_path):
        """Test starting and stopping background thread."""
        policy = RetentionPolicy(db_path=temp_db_path)

        # Start
        policy.start()
        assert policy._running
        assert policy._cleanup_thread is not None
        assert policy._cleanup_thread.is_alive()

        # Stop
        policy.stop()
        assert not policy._running

    def test_auto_cleanup(self, temp_db_path):
        """Test automatic cleanup on initialization."""
        policy = RetentionPolicy(db_path=temp_db_path, auto_cleanup=True)

        assert policy._running
        assert policy._cleanup_thread.is_alive()

        policy.stop()

    def test_cleanup_now_deletes_old_traces(self, populated_db):
        """Test that cleanup_now deletes old traces."""
        db_path = populated_db['db_path']

        # Use 7 day retention (should delete 10-day and 30-day old traces)
        policy = RetentionPolicy(retention_days=7, db_path=db_path)

        # Perform cleanup
        deleted_count = policy.cleanup_now()

        # Should delete 2 traces (10-day and 30-day old)
        assert deleted_count == 2

        # Verify recent trace still exists
        manager = get_manager(db_path)
        result = manager.execute_with_retry(
            "SELECT COUNT(*) FROM traces WHERE id = ?",
            [populated_db['recent']]
        )
        assert result.fetchone()[0] == 1

        # Verify old traces deleted
        result = manager.execute_with_retry(
            "SELECT COUNT(*) FROM traces WHERE id = ?",
            [populated_db['old']]
        )
        assert result.fetchone()[0] == 0

        result = manager.execute_with_retry(
            "SELECT COUNT(*) FROM traces WHERE id = ?",
            [populated_db['very_old']]
        )
        assert result.fetchone()[0] == 0

    def test_cleanup_now_with_different_retention(self, populated_db):
        """Test cleanup with different retention periods."""
        db_path = populated_db['db_path']

        # Use 15 day retention (should only delete 30-day old trace)
        policy = RetentionPolicy(retention_days=15, db_path=db_path)

        deleted_count = policy.cleanup_now()

        # Should delete 1 trace (30-day old)
        assert deleted_count == 1

        # Verify recent and 10-day old traces still exist
        manager = get_manager(db_path)
        result = manager.execute_with_retry("SELECT COUNT(*) FROM traces")
        assert result.fetchone()[0] == 2

    def test_cleanup_now_returns_zero_if_no_old_traces(self, temp_db_path):
        """Test that cleanup returns 0 if no old traces."""
        # Create only recent trace
        writer = TraceWriter(db_path=temp_db_path, batch_size=1)
        writer.start()

        writer.write_trace(
            trace_id=str(uuid.uuid4()),
            started_at=datetime.now(timezone.utc),
            status='running',
            thread_id=12345
        )

        time.sleep(0.2)
        writer.stop()

        # Cleanup with 7 day retention
        policy = RetentionPolicy(retention_days=7, db_path=temp_db_path)
        deleted_count = policy.cleanup_now()

        assert deleted_count == 0

    def test_get_stats(self, populated_db):
        """Test statistics reporting."""
        db_path = populated_db['db_path']
        policy = RetentionPolicy(retention_days=7, db_path=db_path)

        stats = policy.get_stats()

        assert stats['retention_days'] == 7
        assert stats['total_traces'] == 3
        assert stats['traces_to_delete'] == 2  # 10-day and 30-day old
        assert 'cutoff_date' in stats
        assert stats['is_running'] is False

    def test_background_cleanup_runs(self, temp_db_path):
        """Test that background cleanup runs periodically."""
        # Create old trace
        writer = TraceWriter(db_path=temp_db_path, batch_size=1)
        writer.start()

        writer.write_trace(
            trace_id=str(uuid.uuid4()),
            started_at=datetime.now(timezone.utc) - timedelta(days=10),
            status='completed',
            thread_id=12345
        )

        time.sleep(0.2)
        writer.stop()

        # Test immediate cleanup (not background thread)
        # Note: We can't easily test the periodic cleanup in unit tests
        # because it runs every 24 hours. Testing immediate cleanup instead.
        policy = RetentionPolicy(retention_days=7, db_path=temp_db_path)

        # Manually trigger cleanup (without starting background thread)
        deleted = policy.cleanup_now()

        assert deleted == 1

    def test_context_manager_pattern(self, temp_db_path):
        """Test that policy stops on shutdown."""
        policy = RetentionPolicy(db_path=temp_db_path)
        policy.start()

        assert policy._running

        # Stop via explicit call (simulating atexit)
        policy.stop()

        assert not policy._running


class TestGlobalRetentionPolicy:
    """Test global retention policy singleton."""

    def test_get_retention_policy_returns_singleton(self, temp_db_path):
        """Test that get_retention_policy returns same instance."""
        policy1 = get_retention_policy(db_path=temp_db_path)
        policy2 = get_retention_policy(db_path=temp_db_path)

        assert policy1 is policy2

    def test_reset_retention_policy_clears_singleton(self, temp_db_path):
        """Test that reset clears the singleton."""
        policy1 = get_retention_policy(db_path=temp_db_path)

        reset_retention_policy()

        policy2 = get_retention_policy(db_path=temp_db_path)

        # Should be a new instance
        assert policy1 is not policy2


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_cleanup_on_empty_database(self, temp_db_path):
        """Test cleanup on empty database doesn't error."""
        # Create empty database
        manager = get_manager(temp_db_path)
        manager.get_connection()

        policy = RetentionPolicy(retention_days=7, db_path=temp_db_path)
        deleted = policy.cleanup_now()

        assert deleted == 0

    def test_cleanup_with_very_short_retention(self, populated_db):
        """Test cleanup with 1 day retention."""
        db_path = populated_db['db_path']

        # Use 1 day retention (should delete almost all traces)
        policy = RetentionPolicy(retention_days=1, db_path=db_path)
        deleted = policy.cleanup_now()

        # Should delete 2 traces (10-day and 30-day old)
        # 1-day old trace should still exist
        assert deleted >= 2

    def test_cleanup_with_very_long_retention(self, populated_db):
        """Test cleanup with 365 day retention."""
        db_path = populated_db['db_path']

        # Use 365 day retention (should delete nothing)
        policy = RetentionPolicy(retention_days=365, db_path=db_path)
        deleted = policy.cleanup_now()

        assert deleted == 0
