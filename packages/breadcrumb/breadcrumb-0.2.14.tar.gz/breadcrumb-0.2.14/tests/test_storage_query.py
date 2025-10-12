import pytest

from breadcrumb.storage.connection import ConnectionManager, reset_manager
from breadcrumb.storage.query import InvalidQueryError, query_traces


def test_query_traces_select_only(tmp_path):
    db_path = tmp_path / "sample.duckdb"
    reset_manager()
    manager = ConnectionManager(str(db_path))
    with manager.get_connection_context() as conn:
        conn.execute("INSERT INTO traces (id, started_at, ended_at, status, thread_id) VALUES ('t1', NOW(), NOW(), 'completed', 1)")
    rows = query_traces("SELECT * FROM traces", db_path=str(db_path))
    assert rows[0]["status"] == "completed"


def test_query_traces_rejects_non_select():
    with pytest.raises(InvalidQueryError):
        query_traces("DROP TABLE foo")
