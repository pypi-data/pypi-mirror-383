import json
from datetime import datetime, timezone
from pathlib import Path

import duckdb

from breadcrumb.storage.async_writer import TraceWriter
from breadcrumb.storage.connection import ConnectionManager


def test_trace_writer_passes_max_value_size(monkeypatch, tmp_path):
    db_path = tmp_path / "traces.duckdb"
    manager = ConnectionManager(str(db_path))
    conn = manager.get_connection()

    captured_sizes = []

    def fake_truncate_dict(data, max_value_size):
        captured_sizes.append(max_value_size)
        return data

    monkeypatch.setattr("breadcrumb.storage.async_writer.truncate_dict", fake_truncate_dict)

    writer = TraceWriter(db_path=str(db_path), max_value_size=512)
    writer._insert_trace_events(
        conn,
        [
            {
                "event_id": "event-1",
                "trace_id": "trace-1",
                "timestamp": datetime.now(timezone.utc),
                "event_type": "call",
                "function_name": "foo",
                "module_name": "__main__",
                "file_path": str(Path(__file__)),
                "line_number": 10,
                "data": {"payload": "X" * 1024},
            }
        ],
    )

    assert captured_sizes == [512]
