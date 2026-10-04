"""White Team's logic for updating RevisableStrategy mid-episode (e.g. after a
PIVOT). Never touches FrozenConstraints -- enforced at the type level, not
just convention.
"""
from __future__ import annotations

from adapt.schemas import RevisableStrategy


def update_strategy(objective: str, verification_criteria: list[str]) -> RevisableStrategy:
    """Draft an updated revisable tier. Caller swaps it into the active RoEContract."""
    return RevisableStrategy(objective=objective, verification_criteria=verification_criteria)
