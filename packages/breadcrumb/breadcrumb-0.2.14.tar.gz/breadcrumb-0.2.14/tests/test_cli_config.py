from pathlib import Path

import yaml

from breadcrumb.cli.commands import config as config_cmd


def setup_config_dir(monkeypatch, tmp_path):
    config_dir = tmp_path / "config"
    monkeypatch.setattr(config_cmd, "CONFIG_DIR", str(config_dir))
    return config_dir


def test_config_workflow(monkeypatch, tmp_path, capsys):
    config_dir = setup_config_dir(monkeypatch, tmp_path)

    # Create new config
    config_cmd.config_create("pizza", include=["__main__"], force=True)
    config_path = config_cmd._get_config_path("pizza")
    assert Path(config_path).exists()

    data = yaml.safe_load(Path(config_path).read_text())
    assert data["max_repr_length"] == 2000

    # Edit config
    config_cmd.config_edit(
        name="pizza",
        add_include=["flock.*"],
        sample_rate=0.5,
        db_path="/tmp/pizza.duckdb",
        enabled=False,
    )

    updated = yaml.safe_load(Path(config_path).read_text())
    assert updated["include"] == ["__main__", "flock.*"]
    assert updated["sample_rate"] == 0.5
    assert updated["db_path"] == "/tmp/pizza.duckdb"
    assert updated["enabled"] is False

    # Show config
    config_cmd.config_show("pizza")
    output = capsys.readouterr().out
    assert "Configuration: pizza" in output
    assert "max_repr_length" in output

    # List configs
    config_cmd.config_list()
    listing = capsys.readouterr().out
    assert "pizza" in listing

    # Delete config
    config_cmd.config_delete("pizza", force=True)
    assert not Path(config_path).exists()


def test_config_validate(monkeypatch, tmp_path, capsys):
    setup_config_dir(monkeypatch, tmp_path)
    config_cmd.config_create("test", force=True)
    config_cmd.config_validate("test")
    out = capsys.readouterr().out
    assert "Validating config: test" in out
