"""Appends a record every time `constraint_enforcer.check` returns BLOCKED:
what was attempted, which constraint it violated, timestamp.

This is the evidence behind the safety claim in the conclusion -- without
it, "the contract prevents unsafe actions" isn't verifiable after the fact.
"""
from __future__ import annotations


def record(action: dict, reason: str) -> None:
    raise NotImplementedError
