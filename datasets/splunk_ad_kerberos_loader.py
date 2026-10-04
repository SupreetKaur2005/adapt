"""Parses Splunk-format AD attack logs (Event ID 4769 Kerberos ticket requests,
Event ID 4104 PowerShell block logs).

Feeds both `adapt.agents.red_team.tools.kerberoast_tool` (what a realistic
attack sequence looks like) and the Blue Team's detection logic (what to
flag).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ADEvent:
    event_id: int
    host: str
    account_name: str
    raw: dict


def load_kerberos_events(path: Path | str) -> list[ADEvent]:
    raise NotImplementedError
