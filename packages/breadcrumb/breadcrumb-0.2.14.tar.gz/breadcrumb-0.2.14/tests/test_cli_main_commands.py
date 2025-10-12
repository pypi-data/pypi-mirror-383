from pathlib import Path

from typer.testing import CliRunner

from breadcrumb.cli.main import app


def _mock_load_config(monkeypatch, db_path):
    monkeypatch.setattr(
        "breadcrumb.cli.commands.config.load_config",
        lambda name: {"db_path": db_path},
    )


def test_list_uses_config_db_path(monkeypatch, tmp_path):
    runner = CliRunner()
    db_path = str(tmp_path / "traces.duckdb")
    _mock_load_config(monkeypatch, db_path)

    captured = {}

    def fake_execute_list(limit, format, db_path, verbose):
        captured["args"] = (limit, format, db_path, verbose)
        return 0

    monkeypatch.setattr("breadcrumb.cli.commands.list.execute_list", fake_execute_list)

    result = runner.invoke(app, ["list", "-c", "proj"])
    assert result.exit_code == 0
    assert captured["args"][2] == db_path

    # Global --db-path should override config
    result = runner.invoke(app, ["--db-path", "/tmp/override.duckdb", "list", "-c", "proj"])
    assert result.exit_code == 0
    assert captured["args"][2] == "/tmp/override.duckdb"


def test_report_calls_generator(monkeypatch, tmp_path):
    runner = CliRunner()
    db_path = str(tmp_path / "traces.duckdb")
    _mock_load_config(monkeypatch, db_path)

    called = {}

    def fake_report(path):
        called["db_path"] = path

    monkeypatch.setattr("breadcrumb.cli.commands.run._generate_run_report", fake_report)

    result = runner.invoke(app, ["report", "-c", "proj"])
    assert result.exit_code == 0
    assert called["db_path"] == db_path


def test_clear_deletes_db(monkeypatch, tmp_path):
    runner = CliRunner()
    db_file = tmp_path / "project.duckdb"
    db_file.write_text("dummy")
    _mock_load_config(monkeypatch, str(db_file))

    result = runner.invoke(app, ["clear", "-c", "proj", "--force"])
    assert result.exit_code == 0
    assert not db_file.exists()
