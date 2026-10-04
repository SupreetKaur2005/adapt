"""CUV = (exploit_success_rate x stealth_multiplier) / (cost_per_token x execution_time),
keyed by ATT&CK technique.
"""
from __future__ import annotations

from adapt.schemas import AttackTechnique


def compute_cuv(subtask: str, technique: AttackTechnique, candidate_model: str) -> float:
    """Calls `task_estimator.estimate` for the two inputs it can't observe directly
    (success rate, stealth).
    """
    raise NotImplementedError
