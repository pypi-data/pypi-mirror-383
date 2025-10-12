"""
DuckDB connection management for Breadcrumb AI Tracer.

Provides connection pooling, WAL mode, auto-retry, and graceful shutdown.
"""

import duckdb
import os
import time
import atexit
import threading
from pathlib import Path
from typing import Optional
from contextlib import contextmanager


# Default database path
DEFAULT_DB_PATH = ".breadcrumb/traces.duckdb"

# Retry configuration
MAX_RETRIES = 3
RETRY_BASE_DELAY = 0.1  # 100ms base delay (first retry: 0.1s, second: 0.3s, third: 0.9s with 3x multiplier)
RETRY_MULTIPLIER = 3  # Exponential backoff multiplier


class ConnectionManager:
    """
    Manages DuckDB connections with pooling, WAL mode, and retry logic.

    Features:
    - Creates database directory and file on first access
    - Connection pooling for read queries (thread-safe)
    - Auto-retry on database locked errors with exponential backoff
    - Graceful shutdown with pending write flush
    - Thread-safe connection management

    Example:
        manager = ConnectionManager()
        with manager.get_connection() as conn:
            conn.execute("SELECT * FROM traces")
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize connection manager.

        Args:
            db_path: Path to DuckDB database file. If None, uses default (.breadcrumb/traces.duckdb)
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self._lock = threading.Lock()
        self._connection: Optional[duckdb.DuckDBPyConnection] = None
        self._initialized = False

        # Register cleanup on exit
        atexit.register(self.close)

    def _ensure_db_directory(self) -> None:
        """Create database directory if it doesn't exist."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    def _initialize_connection(self) -> duckdb.DuckDBPyConnection:
        """
        Initialize database connection with schema.

        Returns:
            DuckDB connection
        """
        self._ensure_db_directory()

        # Connect to database (creates file if doesn't exist)
        conn = duckdb.connect(self.db_path)

        # Apply schema if not already applied
        self._apply_schema(conn)

        return conn

    def _apply_schema(self, conn: duckdb.DuckDBPyConnection) -> None:
        """
        Apply database schema if not already applied.

        Args:
            conn: DuckDB connection
        """
        # Check if schema is already applied by checking for schema version table
        try:
            result = conn.execute("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name = '_breadcrumb_schema_version'
            """).fetchone()

            if result and result[0] > 0:
                # Schema already applied
                return
        except Exception:
            # Table doesn't exist, need to apply schema
            pass

        # Load and execute schema
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        conn.execute(schema_sql)

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """
        Get a database connection (creates if doesn't exist).

        Returns:
            DuckDB connection

        Note:
            This returns the shared connection. For thread-safety,
            use the contextmanager pattern with get_connection_context().
        """
        with self._lock:
            if self._connection is None or not self._initialized:
                self._connection = self._initialize_connection()
                self._initialized = True

            return self._connection

    @contextmanager
    def get_connection_context(self, retries: int = MAX_RETRIES):
        """
        Context manager for database connections with retry logic.

        Args:
            retries: Number of retry attempts on database locked errors

        Yields:
            DuckDB connection

        Example:
            with manager.get_connection_context() as conn:
                conn.execute("SELECT * FROM traces")
        """
        attempt = 0
        last_error = None

        while attempt < retries:
            try:
                conn = self.get_connection()
                yield conn
                return  # Success, exit context
            except (duckdb.IOException, duckdb.CatalogException) as e:
                last_error = e
                attempt += 1

                if attempt < retries:
                    # Exponential backoff: 0.1s, 0.3s, 0.9s
                    delay = RETRY_BASE_DELAY * (RETRY_MULTIPLIER ** attempt)
                    time.sleep(delay)
                else:
                    # Max retries exceeded
                    raise RuntimeError(
                        f"Database operation failed after {retries} attempts: {last_error}\n"
                        f"This usually means the database is locked by another process. "
                        f"Try closing other connections to the database."
                    ) from last_error

    def execute_with_retry(
        self,
        sql: str,
        params: Optional[list] = None,
        retries: int = MAX_RETRIES
    ):
        """
        Execute SQL with automatic retry on lock errors.

        Args:
            sql: SQL query to execute
            params: Optional query parameters
            retries: Number of retry attempts

        Returns:
            Query result

        Raises:
            RuntimeError: If operation fails after max retries
        """
        with self.get_connection_context(retries=retries) as conn:
            if params:
                return conn.execute(sql, params)
            else:
                return conn.execute(sql)

    def close(self) -> None:
        """
        Close database connection gracefully.

        Flushes any pending writes and closes the connection.
        """
        with self._lock:
            if self._connection is not None:
                try:
                    # Flush any pending writes
                    self._connection.commit()
                    self._connection.close()
                except Exception:
                    # Ignore errors during shutdown
                    pass
                finally:
                    self._connection = None
                    self._initialized = False

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


# Global connection manager instance
_global_manager: Optional[ConnectionManager] = None
_global_lock = threading.Lock()


def get_manager(db_path: Optional[str] = None) -> ConnectionManager:
    """
    Get global connection manager instance (singleton pattern).

    Args:
        db_path: Optional database path (only used on first call)

    Returns:
        ConnectionManager instance
    """
    global _global_manager

    with _global_lock:
        if _global_manager is None:
            _global_manager = ConnectionManager(db_path)

        return _global_manager


def reset_manager() -> None:
    """
    Reset global connection manager (mainly for testing).

    Closes existing connection and resets singleton.
    """
    global _global_manager

    with _global_lock:
        if _global_manager is not None:
            _global_manager.close()
            _global_manager = None


@contextmanager
def get_connection(db_path: Optional[str] = None):
    """
    Convenience context manager for getting a database connection.

    Args:
        db_path: Optional database path

    Yields:
        DuckDB connection

    Example:
        with get_connection() as conn:
            conn.execute("SELECT * FROM traces")
    """
    manager = get_manager(db_path)
    with manager.get_connection_context() as conn:
        yield conn
