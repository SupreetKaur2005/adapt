"""Estimates exploit-success-rate and stealth-multiplier for a given technique.

Two modes:
  - warm: query `adapt.memory.csim_store` for historical PASS rates on
    similar past subtasks.
  - cold-start: a fixed heuristic table keyed by ATT&CK tactic, used when no
    CSIM history exists yet.
"""
from __future__ import annotations

from adapt.schemas import AttackTechnique

# tactic -> (success_rate, stealth_multiplier)
COLD_START_TABLE: dict[str, tuple[float, float]] = {
    "credential-access": (0.5, 0.7),
    "lateral-movement": (0.4, 0.6),
    "discovery": (0.7, 0.9),
}


def estimate(subtask: str, technique: AttackTechnique) -> tuple[float, float]:
    """Return (success_rate, stealth_multiplier) -- warm if CSIM history exists,
    else cold-start from `COLD_START_TABLE`.
    """
    raise NotImplementedError
