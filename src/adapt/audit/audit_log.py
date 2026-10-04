"""Appends a record every time `constraint_enforcer.check` returns BLOCKED:
what was attempted, which constraint it violated, timestamp.

This is the evidence behind the safety claim in the conclusion -- without
it, "the contract prevents unsafe actions" isn't verifiable after the fact.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

_DEFAULT_LOG_PATH = "data/audit/audit_log.jsonl"


def _log_path() -> Path:
    return Path(os.environ.get("AUDIT_LOG_PATH", _DEFAULT_LOG_PATH))


def record(action: dict, reason: str) -> None:
    """what was attempted, which constraint it violated, timestamp."""
    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "reason": reason,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
