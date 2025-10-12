"""
Retention policy enforcement for automatic trace cleanup.

Provides automatic deletion of old traces based on configurable retention period.
"""

import os
import threading
import time
from typing import Optional
from datetime import datetime, timedelta, timezone
import atexit

from breadcrumb.storage.connection import get_manager


# Default retention period in days
DEFAULT_RETENTION_DAYS = 7

# Cleanup interval in seconds (default: daily)
CLEANUP_INTERVAL = 24 * 60 * 60  # 24 hours


class RetentionPolicy:
    """
    Automatic trace retention policy enforcement.

    Features:
    - Configurable retention period (days)
    - Optional background cleanup thread
    - On-demand cleanup via cleanup_now()
    - Thread-safe cleanup operations

    Example:
        policy = RetentionPolicy(retention_days=7)
        policy.start()  # Start background cleanup

        # Or manual cleanup
        policy.cleanup_now()
    """

    def __init__(
        self,
        retention_days: Optional[int] = None,
        db_path: Optional[str] = None,
        auto_cleanup: bool = False,
    ):
        """
        Initialize retention policy.

        Args:
            retention_days: Number of days to retain traces (default from env var or 7)
            db_path: Optional database path
            auto_cleanup: If True, starts background cleanup thread automatically
        """
        # Get retention days from env var if not provided
        if retention_days is None:
            retention_days = int(os.getenv('BREADCRUMB_RETENTION_DAYS', str(DEFAULT_RETENTION_DAYS)))

        self.retention_days = retention_days
        self.db_path = db_path
        self._cleanup_thread: Optional[threading.Thread] = None
        self._running = False
        self._stop_event = threading.Event()

        # Register shutdown hook
        atexit.register(self.stop)

        if auto_cleanup:
            self.start()

    def start(self) -> None:
        """Start background cleanup thread."""
        if self._running:
            return

        self._running = True
        self._stop_event.clear()

        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="breadcrumb-retention"
        )
        self._cleanup_thread.start()

    def stop(self) -> None:
        """Stop background cleanup thread."""
        if not self._running:
            return

        self._stop_event.set()
        self._running = False

        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5.0)

    def cleanup_now(self) -> int:
        """
        Perform cleanup immediately (synchronous).

        Returns:
            Number of traces deleted

        Raises:
            Exception: If cleanup fails
        """
        manager = get_manager(self.db_path)

        # Calculate cutoff date (use UTC to match stored timestamps)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)

        return self._perform_cleanup(manager, cutoff_date)

    def _perform_cleanup(self, manager, cutoff_date: datetime) -> int:
        """
        Perform actual cleanup with proper counting.

        Args:
            manager: Connection manager
            cutoff_date: Delete traces older than this date

        Returns:
            Number of traces deleted
        """
        # First, count how many will be deleted
        count_result = manager.execute_with_retry("""
            SELECT COUNT(*) FROM traces
            WHERE started_at < ?
        """, [cutoff_date])

        row = count_result.fetchone()
        if row is None:
            return 0

        count = row[0]

        if count == 0:
            return 0

        # Delete old traces
        manager.execute_with_retry("""
            DELETE FROM traces
            WHERE started_at < ?
        """, [cutoff_date])

        return count

    def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self._running:
            try:
                # Perform cleanup
                deleted = self.cleanup_now()

                if deleted > 0:
                    import sys
                    print(
                        f"INFO: Breadcrumb retention policy deleted {deleted} traces "
                        f"older than {self.retention_days} days.",
                        file=sys.stderr
                    )

            except Exception as e:
                import sys
                print(f"ERROR: Breadcrumb retention cleanup failed: {e}", file=sys.stderr)

            # Wait for next cleanup interval or stop event
            if self._stop_event.wait(timeout=CLEANUP_INTERVAL):
                break

    def get_stats(self) -> dict:
        """
        Get retention policy statistics.

        Returns:
            Dict with retention settings and trace counts
        """
        manager = get_manager(self.db_path)

        # Total traces
        total_result = manager.execute_with_retry("SELECT COUNT(*) FROM traces")
        total_count = total_result.fetchone()[0]

        # Traces that will be deleted in next cleanup
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
        old_result = manager.execute_with_retry("""
            SELECT COUNT(*) FROM traces
            WHERE started_at < ?
        """, [cutoff_date])
        old_count = old_result.fetchone()[0]

        return {
            'retention_days': self.retention_days,
            'total_traces': total_count,
            'traces_to_delete': old_count,
            'cutoff_date': cutoff_date.isoformat(),
            'is_running': self._running,
        }


# Global retention policy instance
_global_policy: Optional[RetentionPolicy] = None
_global_policy_lock = threading.Lock()


def get_retention_policy(
    retention_days: Optional[int] = None,
    db_path: Optional[str] = None,
    auto_cleanup: bool = False
) -> RetentionPolicy:
    """
    Get global retention policy instance (singleton).

    Args:
        retention_days: Number of days to retain traces
        db_path: Optional database path
        auto_cleanup: If True, starts background cleanup

    Returns:
        RetentionPolicy instance
    """
    global _global_policy

    with _global_policy_lock:
        if _global_policy is None:
            _global_policy = RetentionPolicy(
                retention_days=retention_days,
                db_path=db_path,
                auto_cleanup=auto_cleanup
            )

        return _global_policy


def reset_retention_policy() -> None:
    """Reset global retention policy (for testing)."""
    global _global_policy

    with _global_policy_lock:
        if _global_policy is not None:
            _global_policy.stop()
            _global_policy = None
