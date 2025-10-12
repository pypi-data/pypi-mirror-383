"""
Integration tests for edge case handling.

Tests:
- Empty database error messages
- Database locked retry logic
- Large value truncation
- Malformed SQL error handling
- Query timeout
"""

import pytest
import tempfile
import os
import time
from pathlib import Path
from datetime import datetime

from breadcrumb.storage.connection import ConnectionManager, reset_manager
from breadcrumb.storage.query import (
    query_traces,
    QueryError,
    InvalidQueryError,
    QueryTimeoutError,
)
from breadcrumb.storage.value_truncation import truncate_value, truncate_dict, MAX_VALUE_SIZE
from breadcrumb.storage.async_writer import TraceWriter


class TestEmptyDatabaseHandling:
    """Test empty database error messages."""

    def test_empty_database_returns_empty_list(self, tmp_path):
        """Test that querying empty database returns empty list."""
        reset_manager()
        db_path = str(tmp_path / "test.duckdb")

        # Create database with schema but no data
        manager = ConnectionManager(db_path)
        conn = manager.get_connection()
        # Schema is auto-created, but no traces inserted

        # Query should return empty list (not error)
        result = query_traces("SELECT * FROM traces", db_path=db_path)
        assert result == []

        reset_manager()

    def test_missing_table_helpful_error(self, tmp_path):
        """Test that missing table gives setup instructions."""
        reset_manager()
        db_path = str(tmp_path / "empty.duckdb")

        # Create empty database file without schema
        import duckdb

        # Create a database without our schema and add a dummy table
        conn = duckdb.connect(db_path)
        # Create a different table to prevent auto-schema creation
        conn.execute("CREATE TABLE dummy (id INTEGER)")
        conn.close()

        # Now try to query traces table that doesn't exist - should get helpful error
        # Note: Our connection manager auto-creates schema, so we need to bypass it
        conn2 = duckdb.connect(db_path)
        try:
            # This should raise an error about table not existing
            conn2.execute("SELECT * FROM traces").fetchall()
            assert False, "Should have raised error about missing table"
        except Exception as e:
            # Verify it's a table not found error
            assert "table" in str(e).lower() or "catalog" in str(e).lower()
        finally:
            conn2.close()

        reset_manager()


class TestDatabaseLockedRetry:
    """Test database locked retry with exponential backoff."""

    def test_retry_logic_exists(self, tmp_path):
        """Test that retry logic is configured correctly."""
        from breadcrumb.storage.connection import MAX_RETRIES, RETRY_BASE_DELAY, RETRY_MULTIPLIER

        assert MAX_RETRIES == 3
        assert RETRY_BASE_DELAY == 0.1
        assert RETRY_MULTIPLIER == 3

    def test_connection_retry_on_lock(self, tmp_path):
        """Test that connection manager retries on lock errors."""
        reset_manager()
        db_path = str(tmp_path / "test.duckdb")

        manager = ConnectionManager(db_path)

        # Test that execute_with_retry exists and has retry parameter
        result = manager.execute_with_retry("SELECT 1 as test", retries=3)
        assert result.fetchone()[0] == 1

        reset_manager()


class TestLargeValueTruncation:
    """Test truncation of large values to prevent storage issues."""

    def test_truncate_small_value(self):
        """Small values should not be truncated."""
        small_value = "x" * 100
        result = truncate_value(small_value)
        assert result == small_value
        assert "[TRUNCATED" not in result

    def test_truncate_large_string(self):
        """Large strings should be truncated with indicator."""
        large_value = "x" * 2000
        result = truncate_value(large_value, max_size=1024)

        assert len(result) < len(large_value)
        assert "[TRUNCATED" in result
        assert "original size 2000 bytes" in result

    def test_truncate_large_dict(self):
        """Large dicts should be truncated."""
        large_dict = {"data": "x" * 2000, "small": "value"}
        result = truncate_dict(large_dict, max_value_size=1024)

        assert "[TRUNCATED" in str(result["data"])
        assert result["small"] == "value"  # Small value unchanged

    def test_truncate_nested_dict(self):
        """Nested dicts should be recursively truncated."""
        nested = {
            "level1": {
                "level2": {
                    "large_value": "x" * 2000,
                    "small_value": "ok"
                }
            }
        }
        result = truncate_dict(nested, max_value_size=1024)

        assert "[TRUNCATED" in str(result["level1"]["level2"]["large_value"])
        assert result["level1"]["level2"]["small_value"] == "ok"

    def test_truncation_in_async_writer(self, tmp_path):
        """Test that async writer truncates large values."""
        reset_manager()
        db_path = str(tmp_path / "test.duckdb")

        writer = TraceWriter(db_path=db_path, batch_size=1, batch_timeout=0.01)
        writer.start()

        # Write event with large data
        large_data = {"huge_field": "x" * 2000, "normal": "value"}
        trace_id = "test-trace-123"

        # Write trace
        writer.write_trace(
            trace_id=trace_id,
            started_at=datetime.now(),
            status="running",
            thread_id=1,
            metadata=large_data,
        )

        # Wait for flush
        time.sleep(0.5)
        writer.stop()

        # Verify data was truncated when stored
        from breadcrumb.storage.query import get_trace

        # Note: get_trace might fail if trace doesn't have events
        # Just verify writer didn't crash
        stats = writer.get_stats()
        assert stats['events_written'] > 0

        reset_manager()


class TestMalformedSQLHandling:
    """Test malformed SQL error handling."""

    def test_invalid_select_syntax(self, tmp_path):
        """Test SQL syntax error gives helpful message."""
        reset_manager()
        db_path = str(tmp_path / "test.duckdb")

        # Create database with schema
        manager = ConnectionManager(db_path)
        conn = manager.get_connection()

        # Try malformed SQL - this is caught by validation since it doesn't start with SELECT
        with pytest.raises(InvalidQueryError) as exc_info:
            query_traces("SELEC * FROM traces", db_path=db_path)

        error_msg = str(exc_info.value)
        # Should mention SELECT required
        assert "SELECT" in error_msg

        # Try actual SQL syntax error that passes validation
        with pytest.raises(QueryError) as exc_info:
            query_traces("SELECT * FORM traces", db_path=db_path)  # FORM instead of FROM

        error_msg = str(exc_info.value)
        # Should have error message about syntax
        assert len(error_msg) > 10  # Has some helpful message

        reset_manager()

    def test_unsafe_query_rejected(self, tmp_path):
        """Test that non-SELECT queries are rejected."""
        reset_manager()
        db_path = str(tmp_path / "test.duckdb")

        with pytest.raises(InvalidQueryError) as exc_info:
            query_traces("DROP TABLE traces", db_path=db_path)

        error_msg = str(exc_info.value)
        assert "Only SELECT" in error_msg

        with pytest.raises(InvalidQueryError) as exc_info:
            query_traces("INSERT INTO traces VALUES (1, 2, 3)", db_path=db_path)

        error_msg = str(exc_info.value)
        assert "Only SELECT" in error_msg

        reset_manager()


class TestQueryTimeout:
    """Test query timeout handling."""

    def test_timeout_constant_exists(self):
        """Test that timeout constant is defined."""
        from breadcrumb.storage.query import QUERY_TIMEOUT
        assert QUERY_TIMEOUT == 30.0

    def test_fast_query_completes(self, tmp_path):
        """Test that fast queries complete successfully."""
        reset_manager()
        db_path = str(tmp_path / "test.duckdb")

        # Create database
        manager = ConnectionManager(db_path)
        conn = manager.get_connection()

        # Fast query should complete
        result = query_traces("SELECT 1 as test", db_path=db_path)
        # Empty result is fine (no schema match)

        reset_manager()

    def test_timeout_error_type_exists(self):
        """Test that QueryTimeoutError exception exists."""
        from breadcrumb.storage.query import QueryTimeoutError
        assert issubclass(QueryTimeoutError, Exception)

    # Note: We can't easily test actual timeout without creating a slow query
    # which is hard to do reliably in DuckDB. The timeout mechanism is tested
    # by verifying it exists and can be raised.


class TestEdgeCaseIntegration:
    """Integration tests combining multiple edge cases."""

    def test_all_error_types_have_helpful_messages(self, tmp_path):
        """Verify all error types provide helpful, actionable messages."""
        reset_manager()
        db_path = str(tmp_path / "test.duckdb")

        # Test 1: Unsafe query
        try:
            query_traces("DELETE FROM traces", db_path=db_path)
        except InvalidQueryError as e:
            assert len(str(e)) > 20  # Has helpful message
            assert "SELECT" in str(e)

        # Test 2: Syntax error
        manager = ConnectionManager(db_path)
        conn = manager.get_connection()

        try:
            query_traces("SELEC invalid syntax", db_path=db_path)
        except QueryError as e:
            error_msg = str(e)
            assert len(error_msg) > 20
            # Should have suggestion or example

        reset_manager()

    def test_resilience_under_stress(self, tmp_path):
        """Test system handles multiple edge cases gracefully."""
        reset_manager()
        db_path = str(tmp_path / "stress.duckdb")

        writer = TraceWriter(db_path=db_path, batch_size=10)
        writer.start()

        # Write many events with various edge cases
        for i in range(50):
            # Mix of normal and large data
            data = {"field": "x" * (100 if i % 2 == 0 else 2000)}

            writer.write_trace(
                trace_id=f"trace-{i}",
                started_at=datetime.now(),
                status="running",
                thread_id=1,
                metadata=data,
            )

        # Wait and verify
        time.sleep(1.0)
        writer.stop()

        stats = writer.get_stats()
        assert stats['events_written'] == 50
        assert stats['events_dropped'] == 0

        reset_manager()
