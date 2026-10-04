"""The "vaccine registry": committed exploit/patch pairs from PASS verdicts."""
from __future__ import annotations

from dataclasses import dataclass

from adapt.schemas import ExploitAttempt


@dataclass
class HistoricalRecord:
    exploit: ExploitAttempt
    patch: dict
    outcome: str


def commit(exploit: ExploitAttempt, patch: dict) -> None:
    """Only ever called from a PASS verdict."""
    raise NotImplementedError


def query_similar(subtask: str) -> list[HistoricalRecord]:
    """Used by `adapt.routing.task_estimator`."""
    raise NotImplementedError
