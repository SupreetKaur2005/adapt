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
DEFAULT_COLD_START: tuple[float, float] = (0.3, 0.5)

# Fixed stealth default used for the warm path (CSIM history doesn't track
# stealth per record yet -- revisit once it does).
_WARM_STEALTH_DEFAULT = 0.6


def estimate(subtask: str, technique: AttackTechnique) -> tuple[float, float]:
    """Return (success_rate, stealth_multiplier) -- warm if CSIM history exists,
    else cold-start from `COLD_START_TABLE`.
    """
    from adapt.memory.csim_store import query_similar

    try:
        records = query_similar(subtask)
    except NotImplementedError:
        records = []

    if records:
        pass_count = sum(1 for r in records if r.outcome == "PASS")
        success_rate = pass_count / len(records)
        return success_rate, _WARM_STEALTH_DEFAULT

    return COLD_START_TABLE.get(technique.tactic, DEFAULT_COLD_START)
