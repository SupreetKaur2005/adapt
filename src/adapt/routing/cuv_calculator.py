"""CUV = (exploit_success_rate x stealth_multiplier) / (cost_per_token x execution_time),
keyed by ATT&CK technique.
"""
from __future__ import annotations

from adapt.schemas import AttackTechnique, CUVScore

# Pre-execution execution-time heuristic, by tier -- heavier tiers are slower.
TIER_EXEC_TIME_S: dict[str, float] = {
    "lightweight": 2.0,
    "mid": 5.0,
    "heavy": 12.0,
}


def compute_cuv(subtask: str, technique: AttackTechnique, candidate_model: str) -> float:
    """Calls `task_estimator.estimate` for the two inputs it can't observe directly
    (success rate, stealth).
    """
    from adapt.routing.model_router import load_registry, tier_for_model
    from adapt.routing.task_estimator import estimate

    success_rate, stealth_multiplier = estimate(subtask, technique)

    tier = tier_for_model(candidate_model)
    cost_per_token = load_registry()["tiers"][tier]["cost_per_token"]
    execution_time_s = TIER_EXEC_TIME_S[tier]

    score = CUVScore(
        technique_id=technique.technique_id,
        success_rate=success_rate,
        stealth_multiplier=stealth_multiplier,
        cost_per_token=cost_per_token,
        execution_time_s=execution_time_s,
    )
    return score.value
