import json
from datetime import datetime, timezone

import duckdb

from breadcrumb.storage.connection import reset_manager
from breadcrumb.storage.smart_queries import call_query, flow_query, gaps_query


def build_db(tmp_path):
    db_path = tmp_path / "trace.duckdb"
    conn = duckdb.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE traces (
            id VARCHAR PRIMARY KEY,
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            status VARCHAR,
            thread_id BIGINT,
            metadata JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.execute(
        """
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
        """
    )
    conn.close()
    return db_path


def seed_trace(db_path, trace_id="trace-1"):
    conn = duckdb.connect(str(db_path))
    now = datetime.now(timezone.utc)
    conn.execute(
        "INSERT INTO traces (id, started_at, ended_at, status, thread_id) VALUES (?, ?, ?, ?, ?)",
        [trace_id, now, now, "completed", 1],
    )

    def insert(event_id, event_type, fn, module, offset, data=None):
        conn.execute(
            "INSERT INTO trace_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
            [
                event_id,
                trace_id,
                now.replace(microsecond=offset),
                event_type,
                fn,
                module,
                "file.py",
                10,
                json.dumps(data) if data else None,
            ],
        )

    insert("call-main", "call", "main", "__main__", 1, {"args": {}})
    insert("call-child", "call", "child", "__main__", 2, {"args": {"x": 1}})
    insert("return-child", "return", "child", "__main__", 3, {"return_value": 99})
    insert("return-main", "return", "main", "__main__", 4, {"return_value": 99})
    insert("call-child-init", "call", "child.__init__", "__main__", 5, {"args": {}, "kwargs": {"color": "blue"}})
    insert("return-child-init", "return", "child.__init__", "__main__", 6, {"return_value": "child instance"})
    insert(
        "call-site",
        "call_site",
        "external_func",
        "external",
        5,
        {"called_from_function": "main", "called_from_module": "__main__"},
    )

    conn.close()


def test_call_query(tmp_path):
    reset_manager()
    db_path = build_db(tmp_path)
    seed_trace(db_path)

    result = call_query(db_path=str(db_path), function_name="child")
    assert result["function"] == "__main__.child"
    assert set(result.get("matched_functions", [])) == {
        "__main__.child",
        "__main__.child.__init__",
    }
    call_functions = {call["function"] for call in result["calls"]}
    assert "__main__.child" in call_functions
    assert "__main__.child.__init__" in call_functions

    primary = next(call for call in result["calls"] if call["function"] == "__main__.child")
    assert primary["args"]["x"] == 1
    assert primary["return_value"] == 99
    assert primary["called_by"].endswith("main")
    assert primary["duration_ms"] >= 0

    ctor = next(call for call in result["calls"] if call["function"] == "__main__.child.__init__")
    assert ctor["args"].get("color") == "blue"
    assert ctor["return_value"] == "child instance"


def test_flow_query(tmp_path):
    reset_manager()
    db_path = build_db(tmp_path)
    seed_trace(db_path)

    result = flow_query(db_path=str(db_path))
    assert len(result["flow"]) >= 4
    assert any(event["event_type"] == "call" for event in result["flow"])


def test_gaps_query(tmp_path):
    reset_manager()
    db_path = build_db(tmp_path)
    seed_trace(db_path)

    result = gaps_query(db_path=str(db_path))
    assert result["untraced_calls"][0]["function"].startswith("external")


def test_call_query_partial_match(tmp_path):
    reset_manager()
    db_path = build_db(tmp_path)
    seed_trace(db_path)

    result = call_query(db_path=str(db_path), function_name="__main__.")
    assert "matched_functions" in result
    assert set(result["matched_functions"]) >= {
        "__main__.child",
        "__main__.child.__init__",
    }
    assert any(call["function"] == "__main__.child" for call in result["calls"])
