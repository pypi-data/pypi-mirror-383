from typer.testing import CliRunner

from breadcrumb.cli.main import app


def test_query_fuzzy(monkeypatch):
    runner = CliRunner()

    monkeypatch.setattr(
        "breadcrumb.cli.commands.config.load_config",
        lambda name: {"db_path": "/tmp/pizza.duckdb"},
    )

    def fake_fuzzy_query(db_path=None, term=""):
        assert db_path == "/tmp/pizza.duckdb"
        return {"term": term, "matches": [{"function": "pizza_master"}], "total_matches": 1}

    monkeypatch.setattr("breadcrumb.cli.commands.smart_query.fuzzy_query", fake_fuzzy_query)

    result = runner.invoke(app, ["query", "-c", "pizza", "--fuzzy", "Margherita"])
    assert result.exit_code == 0
    # Output should include the fuzzy term and the mocked function name
    assert '"term": "Margherita"' in result.stdout
    assert "pizza_master" in result.stdout


def test_query_sql_disable_truncation(monkeypatch):
    runner = CliRunner()

    monkeypatch.setattr(
        "breadcrumb.cli.commands.config.load_config",
        lambda name: {"db_path": "/tmp/myapp.duckdb"},
    )

    captured = {}

    def fake_execute_query(sql, format, db_path, verbose, disable_truncation):
        captured["sql"] = sql
        captured["format"] = format
        captured["db_path"] = db_path
        captured["disable_truncation"] = disable_truncation
        return 0

    monkeypatch.setattr("breadcrumb.cli.commands.query.execute_query", fake_execute_query)

    result = runner.invoke(
        app,
        [
            "--format",
            "table",
            "query",
            "-c",
            "myapp",
            "--disable-truncation",
            "SELECT 1",
        ],
    )

    assert result.exit_code == 0
    assert captured["sql"] == "SELECT 1"
    assert captured["format"] == "table"
    assert captured["db_path"] == "/tmp/myapp.duckdb"
    assert captured["disable_truncation"] is True
