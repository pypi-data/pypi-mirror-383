import sys
from pathlib import Path

import pytest

from breadcrumb.cli.commands.run import run_command

import subprocess  # noqa: F401 (ensures module is available for monkeypatch)


class FakeResult:
    returncode = 0


def test_run_command_injects_max_chars(monkeypatch, tmp_path):
    script_path = tmp_path / "script.py"
    script_path.write_text("print('ok')\n")

    executed = {}

    def fake_run(cmd, timeout, **kwargs):
        executed["cmd"] = cmd
        wrapper_path = Path(cmd[-1])
        executed["wrapper_content"] = wrapper_path.read_text()
        return FakeResult()

    monkeypatch.setattr("breadcrumb.cli.commands.run.subprocess.run", fake_run)

    exit_codes = []

    def fake_exit(code):
        exit_codes.append(code)
        raise SystemExit(code)

    monkeypatch.setattr(sys, "exit", fake_exit)

    with pytest.raises(SystemExit):
        run_command(
            command=["python", str(script_path)],
            timeout=5,
            max_repr_length=5000,
        )

    assert exit_codes == [0]
    assert executed["cmd"][0].endswith("python") or executed["cmd"][0].endswith("python3")
    assert executed["cmd"][-1] != str(script_path)
    # Wrapper should include the desired max_repr_length argument.
    assert "max_repr_length=5000" in executed["wrapper_content"]
