"""Tests for `adapt.audit.audit_log`."""
import json

from adapt.audit.audit_log import record


def test_record_appends_json_line(tmp_path, monkeypatch):
    log_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("AUDIT_LOG_PATH", str(log_path))

    record({"tool": "rodc_dump", "target_host": "dc01"}, "violates absolute rule")

    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["reason"] == "violates absolute rule"
    assert entry["action"]["tool"] == "rodc_dump"
    assert "timestamp" in entry
