from typing import List

import pytest

from breadcrumb.cli.commands import query as query_cmd


class DummyResult(List[dict]):
    pass


def test_execute_query_table_disable_truncation(monkeypatch, capsys):
    def fake_query_traces(sql, params=None, db_path=None):
        return DummyResult([{"col": "value that is quite long"}])

    monkeypatch.setattr(query_cmd, "query_traces", fake_query_traces)

    exit_code = query_cmd.execute_query(
        sql="SELECT 1",
        format="table",
        db_path="/tmp/db.duckdb",
        verbose=False,
        disable_truncation=True,
    )

    assert exit_code == query_cmd.EXIT_SUCCESS
    output = capsys.readouterr().out
    assert "value that is quite long" in output


def test_execute_query_invalid(monkeypatch):
    def fake_query_traces(sql, params=None, db_path=None):
        raise query_cmd.InvalidQueryError("bad")

    monkeypatch.setattr(query_cmd, "query_traces", fake_query_traces)

    exit_code = query_cmd.execute_query("DROP TABLE foo")
    assert exit_code == query_cmd.EXIT_ERROR
