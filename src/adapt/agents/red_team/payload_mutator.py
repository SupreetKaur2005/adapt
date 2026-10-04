"""Mutates a candidate exploit across attempts, seeded by Atomic Red Team
playbooks so mutations stay realistic rather than arbitrary. Triggered
specifically on a PIVOT outcome.
"""
from __future__ import annotations

from adapt.schemas import ExploitAttempt


def mutate(exploit: ExploitAttempt, technique_id: str) -> ExploitAttempt:
    raise NotImplementedError
