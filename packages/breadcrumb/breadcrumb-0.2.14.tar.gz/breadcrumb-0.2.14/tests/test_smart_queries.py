import json
from datetime import datetime

import duckdb

from breadcrumb.storage.smart_queries import fuzzy_query


def test_fuzzy_query_returns_matches(tmp_path):
    db_path = tmp_path / "traces.duckdb"
    conn = duckdb.connect(str(db_path))
    conn.execute("""
        CREATE TABLE traces (
            id VARCHAR PRIMARY KEY,
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            status VARCHAR,
            thread_id BIGINT,
            metadata JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.execute("""
        CREATE TABLE trace_events (
            id VARCHAR PRIMARY KEY,
            trace_id VARCHAR,
            timestamp TIMESTAMP,
            event_type VARCHAR,
            function_name VARCHAR,
            module_name VARCHAR,
            file_path VARCHAR,
            line_number INTEGER,
            data JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    trace_id = "trace-1"
    conn.execute(
        "INSERT INTO traces (id, started_at, ended_at, status, thread_id) VALUES (?, ?, ?, ?, ?)",
        [trace_id, datetime.utcnow(), datetime.utcnow(), "completed", 1],
    )

    payload = {
        "args": {"recipe": "Breadcrumb pizza with mozzarella"},
    }
    conn.execute(
        "INSERT INTO trace_events (id, trace_id, timestamp, event_type, function_name, module_name, data) VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            "event-1",
            trace_id,
            datetime.utcnow(),
            "call",
            "pizza_master",
            "__main__",
            json.dumps(payload),
        ],
    )

    result = fuzzy_query(db_path=str(db_path), term="mozzarella")
    assert result["term"] == "mozzarella"
    assert result["total_matches"] == 1
    assert result["matches"][0]["function"] == "pizza_master"


def test_fuzzy_query_empty_term():
    result = fuzzy_query(db_path=None, term="   ")
    assert result["message"] == "Empty search term"
    assert result["matches"] == []
