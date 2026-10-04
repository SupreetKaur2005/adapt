"""Parses Atomic Red Team's YAML test definitions from the cloned repo.

Used by `adapt.agents.red_team.payload_mutator` to seed realistic attack
variants rather than generating exploits from nothing.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AtomicTest:
    technique_id: str
    name: str
    command: str
    platform: str


def load_playbooks(technique_id: str) -> list[AtomicTest]:
    raise NotImplementedError
