"""
Tests for query interface.

Validates:
- SQL safety checks
- Query execution
- Error handling
- Time range parsing
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta, timezone
import uuid

from breadcrumb.storage.query import (
    query_traces,
    get_trace,
    find_exceptions,
    analyze_performance,
    InvalidQueryError,
    TraceNotFoundError,
    QueryError,
    _parse_time_range,
    _validate_sql_safe,
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


@pytest.fixture
def populated_db(temp_db_path):
    """Create database with sample data."""
    writer = TraceWriter(db_path=temp_db_path, batch_size=1)
    writer.start()

    # Add sample traces
    trace_id1 = str(uuid.uuid4())
    writer.write_trace(
        trace_id=trace_id1,
        started_at=datetime.now(timezone.utc),
        status='completed',
        thread_id=12345
    )

    writer.write_trace_event(
        event_id=str(uuid.uuid4()),
        trace_id=trace_id1,
        timestamp=datetime.now(timezone.utc),
        event_type='call',
        function_name='test_func',
        module_name='__main__'
    )

    import time
    time.sleep(0.2)
    writer.stop()

    return temp_db_path


class TestSQLSafety:
    """Test SQL safety validation."""

    def test_validate_select_query(self):
        """Test that SELECT queries are allowed."""
        _validate_sql_safe("SELECT * FROM traces")
        _validate_sql_safe("select * from traces")  # case insensitive

    def test_reject_insert_query(self):
        """Test that INSERT queries are rejected."""
        with pytest.raises(InvalidQueryError):
            _validate_sql_safe("INSERT INTO traces VALUES (...)")

    def test_reject_update_query(self):
        """Test that UPDATE queries are rejected."""
        with pytest.raises(InvalidQueryError):
            _validate_sql_safe("UPDATE traces SET status = 'done'")

    def test_reject_delete_query(self):
        """Test that DELETE queries are rejected."""
        with pytest.raises(InvalidQueryError):
            _validate_sql_safe("DELETE FROM traces")

    def test_reject_drop_query(self):
        """Test that DROP queries are rejected."""
        with pytest.raises(InvalidQueryError):
            _validate_sql_safe("DROP TABLE traces")

    def test_reject_non_select_start(self):
        """Test that queries must start with SELECT."""
        with pytest.raises(InvalidQueryError):
            _validate_sql_safe("EXPLAIN SELECT * FROM traces")


class TestTimeRangeParsing:
    """Test time range parsing."""

    def test_parse_minutes(self):
        """Test parsing minutes."""
        result = _parse_time_range("30m")
        expected = datetime.now() - timedelta(minutes=30)
        assert abs((result - expected).total_seconds()) < 2

    def test_parse_hours(self):
        """Test parsing hours."""
        result = _parse_time_range("2h")
        expected = datetime.now() - timedelta(hours=2)
        assert abs((result - expected).total_seconds()) < 2

    def test_parse_days(self):
        """Test parsing days."""
        result = _parse_time_range("1d")
        expected = datetime.now() - timedelta(days=1)
        assert abs((result - expected).total_seconds()) < 2

    def test_parse_iso_date(self):
        """Test parsing ISO date."""
        result = _parse_time_range("2025-01-10")
        expected = datetime(2025, 1, 10)
        assert result.date() == expected.date()

    def test_parse_iso_datetime(self):
        """Test parsing ISO datetime."""
        result = _parse_time_range("2025-01-10T15:30:00Z")
        expected = datetime(2025, 1, 10, 15, 30, 0)
        assert abs((result - expected).total_seconds()) < 2

    def test_invalid_time_range(self):
        """Test invalid time range."""
        with pytest.raises(ValueError):
            _parse_time_range("invalid")


class TestQueryTraces:
    """Test query_traces function."""

    def test_simple_query(self, populated_db):
        """Test simple SELECT query."""
        results = query_traces(
            "SELECT * FROM traces LIMIT 10",
            db_path=populated_db
        )

        assert isinstance(results, list)
        assert len(results) >= 1

    def test_parameterized_query(self, populated_db):
        """Test query with parameters."""
        results = query_traces(
            "SELECT * FROM traces WHERE status = ?",
            params=['completed'],
            db_path=populated_db
        )

        assert isinstance(results, list)
        for row in results:
            assert row['status'] == 'completed'

    def test_unsafe_query_rejected(self, populated_db):
        """Test that unsafe queries are rejected."""
        with pytest.raises(InvalidQueryError):
            query_traces(
                "DELETE FROM traces",
                db_path=populated_db
            )


class TestGetTrace:
    """Test get_trace function."""

    def test_get_existing_trace(self, populated_db):
        """Test getting an existing trace."""
        # First get a trace ID
        results = query_traces(
            "SELECT id FROM traces LIMIT 1",
            db_path=populated_db
        )
        assert len(results) > 0

        trace_id = results[0]['id']

        # Get full trace
        trace_data = get_trace(trace_id, db_path=populated_db)

        assert 'trace' in trace_data
        assert 'events' in trace_data
        assert 'exceptions' in trace_data
        assert trace_data['trace']['id'] == trace_id

    def test_get_nonexistent_trace(self, populated_db):
        """Test getting a non-existent trace."""
        with pytest.raises(TraceNotFoundError):
            get_trace("00000000-0000-0000-0000-000000000000", db_path=populated_db)


class TestFindExceptions:
    """Test find_exceptions function."""

    def test_find_recent_exceptions(self, temp_db_path):
        """Test finding recent exceptions."""
        # Create trace with exception
        writer = TraceWriter(db_path=temp_db_path, batch_size=3)
        writer.start()

        trace_id = str(uuid.uuid4())
        event_id = str(uuid.uuid4())

        writer.write_trace(
            trace_id=trace_id,
            started_at=datetime.now(timezone.utc),
            status='failed',
            thread_id=12345
        )

        writer.write_trace_event(
            event_id=event_id,
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc),
            event_type='exception',
            function_name='test_func'
        )

        writer.write_exception(
            exception_id=str(uuid.uuid4()),
            event_id=event_id,
            trace_id=trace_id,
            exception_type='ValueError',
            message='Test error'
        )

        import time
        time.sleep(0.3)
        writer.stop()

        # Find exceptions
        result = find_exceptions(since="1h", limit=10, db_path=temp_db_path)

        assert 'exceptions' in result
        assert 'total' in result
        assert result['total'] >= 1
        assert len(result['exceptions']) >= 1


class TestAnalyzePerformance:
    """Test analyze_performance function."""

    def test_analyze_function_performance(self, populated_db):
        """Test analyzing function performance."""
        result = analyze_performance(
            function='test_func',
            limit=5,
            db_path=populated_db
        )

        assert 'stats' in result
        assert 'slowest_traces' in result
        assert 'function' in result
        assert result['function'] == 'test_func'

    def test_analyze_nonexistent_function(self, populated_db):
        """Test analyzing non-existent function."""
        result = analyze_performance(
            function='nonexistent_func',
            limit=5,
            db_path=populated_db
        )

        assert result['stats'] is None
        assert len(result['slowest_traces']) == 0
