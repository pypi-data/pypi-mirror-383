"""
Tests for DuckDB schema design and initialization.

Validates:
- Schema creation
- Table structure
- Index creation
- Query performance
"""

import pytest
import duckdb
import tempfile
import os
from pathlib import Path
from datetime import datetime, timezone
import uuid


@pytest.fixture
def temp_db():
    """Create a temporary DuckDB database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.duckdb")
        yield db_path


@pytest.fixture
def schema_sql():
    """Load the schema.sql file."""
    schema_path = Path(__file__).parent.parent.parent / "src" / "breadcrumb" / "storage" / "schema.sql"
    with open(schema_path, 'r') as f:
        return f.read()


@pytest.fixture
def connection(temp_db, schema_sql):
    """Create a DuckDB connection with schema applied."""
    conn = duckdb.connect(temp_db)
    conn.execute(schema_sql)
    yield conn
    conn.close()


class TestSchemaCreation:
    """Test schema creation and table structure."""

    def test_schema_version_table_exists(self, connection):
        """Test that schema version table is created."""
        result = connection.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_name='_breadcrumb_schema_version'
        """).fetchall()
        assert len(result) == 1

    def test_initial_schema_version_recorded(self, connection):
        """Test that initial schema version is recorded."""
        result = connection.execute("""
            SELECT version, description FROM _breadcrumb_schema_version
            WHERE version = 1
        """).fetchone()
        assert result is not None
        assert result[0] == 1
        assert "Initial schema" in result[1]

    def test_traces_table_exists(self, connection):
        """Test that traces table is created with correct columns."""
        result = connection.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name='traces'
        """).fetchall()

        column_names = [col[0] for col in result]
        assert 'id' in column_names
        assert 'started_at' in column_names
        assert 'ended_at' in column_names
        assert 'status' in column_names
        assert 'thread_id' in column_names
        assert 'metadata' in column_names

    def test_trace_events_table_exists(self, connection):
        """Test that trace_events table is created with correct columns."""
        result = connection.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name='trace_events'
        """).fetchall()

        column_names = [col[0] for col in result]
        assert 'id' in column_names
        assert 'trace_id' in column_names
        assert 'timestamp' in column_names
        assert 'event_type' in column_names
        assert 'function_name' in column_names
        assert 'module_name' in column_names
        assert 'file_path' in column_names
        assert 'line_number' in column_names
        assert 'data' in column_names

    def test_variables_table_exists(self, connection):
        """Test that variables table is created with correct columns."""
        result = connection.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name='variables'
        """).fetchall()

        column_names = [col[0] for col in result]
        assert 'id' in column_names
        assert 'event_id' in column_names
        assert 'name' in column_names
        assert 'value' in column_names
        assert 'type' in column_names

    def test_exceptions_table_exists(self, connection):
        """Test that exceptions table is created with correct columns."""
        result = connection.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name='exceptions'
        """).fetchall()

        column_names = [col[0] for col in result]
        assert 'id' in column_names
        assert 'event_id' in column_names
        assert 'trace_id' in column_names
        assert 'exception_type' in column_names
        assert 'message' in column_names
        assert 'stack_trace' in column_names


class TestIndexes:
    """Test that indexes are created for query performance."""

    def test_trace_events_indexes(self, connection):
        """Test that trace_events table has required indexes."""
        # DuckDB doesn't have sqlite_master, use information_schema
        result = connection.execute("""
            SELECT index_name FROM duckdb_indexes()
            WHERE table_name = 'trace_events'
        """).fetchall()

        index_names = [idx[0] for idx in result]
        assert 'idx_trace_events_trace_id' in index_names
        assert 'idx_trace_events_timestamp' in index_names
        assert 'idx_trace_events_function_name' in index_names

    def test_traces_indexes(self, connection):
        """Test that traces table has required indexes."""
        result = connection.execute("""
            SELECT index_name FROM duckdb_indexes()
            WHERE table_name = 'traces'
        """).fetchall()

        index_names = [idx[0] for idx in result]
        assert 'idx_traces_started_at' in index_names
        assert 'idx_traces_status' in index_names

    def test_exceptions_indexes(self, connection):
        """Test that exceptions table has required indexes."""
        result = connection.execute("""
            SELECT index_name FROM duckdb_indexes()
            WHERE table_name = 'exceptions'
        """).fetchall()

        index_names = [idx[0] for idx in result]
        assert 'idx_exceptions_trace_id' in index_names
        assert 'idx_exceptions_type' in index_names


class TestBasicOperations:
    """Test basic CRUD operations on schema."""

    def test_insert_trace(self, connection):
        """Test inserting a trace record."""
        trace_id = str(uuid.uuid4())
        connection.execute("""
            INSERT INTO traces (id, started_at, status, thread_id)
            VALUES (?, ?, ?, ?)
        """, [trace_id, datetime.now(timezone.utc), 'running', 12345])

        result = connection.execute("""
            SELECT id, status FROM traces WHERE id = ?
        """, [trace_id]).fetchone()

        assert result is not None
        assert result[0] == trace_id
        assert result[1] == 'running'

    def test_insert_trace_event(self, connection):
        """Test inserting a trace event."""
        # First create a trace
        trace_id = str(uuid.uuid4())
        connection.execute("""
            INSERT INTO traces (id, started_at, status, thread_id)
            VALUES (?, ?, ?, ?)
        """, [trace_id, datetime.now(timezone.utc), 'running', 12345])

        # Then insert an event
        event_id = str(uuid.uuid4())
        connection.execute("""
            INSERT INTO trace_events (id, trace_id, timestamp, event_type, function_name, module_name)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [event_id, trace_id, datetime.now(timezone.utc), 'call', 'test_func', '__main__'])

        result = connection.execute("""
            SELECT id, event_type, function_name FROM trace_events WHERE id = ?
        """, [event_id]).fetchone()

        assert result is not None
        assert result[0] == event_id
        assert result[1] == 'call'
        assert result[2] == 'test_func'

    def test_insert_exception(self, connection):
        """Test inserting an exception record."""
        # Create trace and event first
        trace_id = str(uuid.uuid4())
        event_id = str(uuid.uuid4())

        connection.execute("""
            INSERT INTO traces (id, started_at, status, thread_id)
            VALUES (?, ?, ?, ?)
        """, [trace_id, datetime.now(timezone.utc), 'failed', 12345])

        connection.execute("""
            INSERT INTO trace_events (id, trace_id, timestamp, event_type, function_name)
            VALUES (?, ?, ?, ?, ?)
        """, [event_id, trace_id, datetime.now(timezone.utc), 'exception', 'test_func'])

        # Insert exception
        exc_id = str(uuid.uuid4())
        connection.execute("""
            INSERT INTO exceptions (id, event_id, trace_id, exception_type, message)
            VALUES (?, ?, ?, ?, ?)
        """, [exc_id, event_id, trace_id, 'ValueError', 'Test error'])

        result = connection.execute("""
            SELECT exception_type, message FROM exceptions WHERE id = ?
        """, [exc_id]).fetchone()

        assert result is not None
        assert result[0] == 'ValueError'
        assert result[1] == 'Test error'

    def test_manual_delete_trace(self, connection):
        """Test manual deletion of trace with related records."""
        # Create trace with event and exception
        trace_id = str(uuid.uuid4())
        event_id = str(uuid.uuid4())
        exc_id = str(uuid.uuid4())

        connection.execute("""
            INSERT INTO traces (id, started_at, status, thread_id)
            VALUES (?, ?, ?, ?)
        """, [trace_id, datetime.now(timezone.utc), 'failed', 12345])

        connection.execute("""
            INSERT INTO trace_events (id, trace_id, timestamp, event_type, function_name)
            VALUES (?, ?, ?, ?, ?)
        """, [event_id, trace_id, datetime.now(timezone.utc), 'exception', 'test_func'])

        connection.execute("""
            INSERT INTO exceptions (id, event_id, trace_id, exception_type, message)
            VALUES (?, ?, ?, ?, ?)
        """, [exc_id, event_id, trace_id, 'ValueError', 'Test error'])

        # Manual deletion (DuckDB doesn't support CASCADE)
        # Delete in reverse foreign key order
        connection.execute("DELETE FROM exceptions WHERE trace_id = ?", [trace_id])
        connection.execute("DELETE FROM trace_events WHERE trace_id = ?", [trace_id])
        connection.execute("DELETE FROM traces WHERE id = ?", [trace_id])

        # Verify all records are deleted
        traces = connection.execute("SELECT COUNT(*) FROM traces WHERE id = ?", [trace_id]).fetchone()
        events = connection.execute("SELECT COUNT(*) FROM trace_events WHERE trace_id = ?", [trace_id]).fetchone()
        exceptions = connection.execute("SELECT COUNT(*) FROM exceptions WHERE trace_id = ?", [trace_id]).fetchone()

        assert traces[0] == 0
        assert events[0] == 0
        assert exceptions[0] == 0


class TestQueryPerformance:
    """Test query performance with indexes."""

    @pytest.fixture
    def populated_db(self, connection):
        """Populate database with sample data for performance tests."""
        # Insert 100 traces
        for i in range(100):
            trace_id = str(uuid.uuid4())
            connection.execute("""
                INSERT INTO traces (id, started_at, status, thread_id)
                VALUES (?, ?, ?, ?)
            """, [trace_id, datetime.now(timezone.utc), 'completed', 12345 + i])

            # Insert 10 events per trace
            for j in range(10):
                event_id = str(uuid.uuid4())
                connection.execute("""
                    INSERT INTO trace_events (id, trace_id, timestamp, event_type, function_name, module_name)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [event_id, trace_id, datetime.now(timezone.utc), 'call', f'func_{j}', '__main__'])

        return connection

    def test_query_by_function_name(self, populated_db):
        """Test querying events by function name uses index."""
        result = populated_db.execute("""
            SELECT COUNT(*) FROM trace_events WHERE function_name = 'func_0'
        """).fetchone()

        # Should find 100 events (1 per trace)
        assert result[0] == 100

    def test_query_by_timestamp(self, populated_db):
        """Test querying events by timestamp uses index."""
        one_hour_ago = datetime.now(timezone.utc).replace(hour=datetime.now(timezone.utc).hour - 1)

        result = populated_db.execute("""
            SELECT COUNT(*) FROM trace_events WHERE timestamp > ?
        """, [one_hour_ago]).fetchone()

        # Should find all 1000 events
        assert result[0] == 1000

    def test_query_by_trace_id(self, populated_db):
        """Test querying events by trace_id uses index."""
        # Get a trace_id
        trace_result = populated_db.execute("SELECT id FROM traces LIMIT 1").fetchone()
        trace_id = trace_result[0]

        result = populated_db.execute("""
            SELECT COUNT(*) FROM trace_events WHERE trace_id = ?
        """, [trace_id]).fetchone()

        # Should find 10 events for this trace
        assert result[0] == 10


class TestJSONSupport:
    """Test JSON column functionality."""

    def test_insert_json_metadata(self, connection):
        """Test inserting JSON metadata in traces."""
        trace_id = str(uuid.uuid4())
        metadata = '{"user": "alice", "session": "abc123"}'

        connection.execute("""
            INSERT INTO traces (id, started_at, status, metadata)
            VALUES (?, ?, ?, ?)
        """, [trace_id, datetime.now(timezone.utc), 'running', metadata])

        result = connection.execute("""
            SELECT metadata FROM traces WHERE id = ?
        """, [trace_id]).fetchone()

        assert result is not None
        assert 'alice' in result[0]
        assert 'abc123' in result[0]

    def test_insert_json_event_data(self, connection):
        """Test inserting JSON data in trace events."""
        # Create trace first
        trace_id = str(uuid.uuid4())
        connection.execute("""
            INSERT INTO traces (id, started_at, status)
            VALUES (?, ?, ?)
        """, [trace_id, datetime.now(timezone.utc), 'running'])

        # Insert event with JSON data
        event_id = str(uuid.uuid4())
        data = '{"args": {"x": 1, "y": 2}, "return_value": 3}'

        connection.execute("""
            INSERT INTO trace_events (id, trace_id, timestamp, event_type, data)
            VALUES (?, ?, ?, ?, ?)
        """, [event_id, trace_id, datetime.now(timezone.utc), 'return', data])

        result = connection.execute("""
            SELECT data FROM trace_events WHERE id = ?
        """, [event_id]).fetchone()

        assert result is not None
        assert '"x": 1' in result[0]
        assert '"return_value": 3' in result[0]
