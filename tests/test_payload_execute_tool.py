"""Tests for `adapt.agents.red_team.tools.payload_execute_tool`."""
from adapt.agents.red_team.tools import payload_execute_tool


class _FakeCompletedProcess:
    def __init__(self, returncode=0, stdout="ok\n", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_payload_execute_runs_inside_target_container(monkeypatch):
    calls = {}

    def fake_run(args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs
        return _FakeCompletedProcess()

    monkeypatch.setattr(payload_execute_tool.subprocess, "run", fake_run)

    result = payload_execute_tool.payload_execute("ws01", "whoami")

    assert calls["args"] == ["docker", "exec", "ws01", "sh", "-c", "whoami"]
    assert result == {"target_host": "ws01", "exit_code": 0, "stdout": "ok\n", "stderr": ""}
