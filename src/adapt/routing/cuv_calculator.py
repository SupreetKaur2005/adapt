"""CUV = (exploit_success_rate x stealth_multiplier) / (cost_per_token x execution_time),
keyed by ATT&CK technique.
# optimized
"""
from __future__ import annotations

from adapt.schemas import AttackTechnique, CUVScore

# Pre-execution execution-time heuristic, by tier -- heavier tiers are slower.
TIER_EXEC_TIME_S: dict[str, float] = {
    "lightweight": 2.0,
    "mid": 5.0,
    "heavy": 12.0,
}

# Cache for CUV scores: (subtask, technique_id, candidate_model) -> score
_cuv_cache: dict[tuple[str, str, str], float] = {}


def _make_cache_key(subtask: str, technique: AttackTechnique, candidate_model: str) -> tuple[str, str, str]:
    return (subtask, technique.technique_id, candidate_model)





def compute_cuv(subtask: str, technique: AttackTechnique, candidate_model: str) -> float:
    """Calls `task_estimator.estimate` for the two inputs it can't observe directly
    (success rate, stealth).
    
    Caches results to avoid redundant CSIM queries and CUV computations.
    """
    from adapt.routing.task_estimator import estimate

    cache_key = (subtask, technique.technique_id, candidate_model)
    if cache_key in _cuv_cache:
        return _cuv_cache[cache_key]

    success_rate, stealth_multiplier = estimate(subtask, technique)

    from adapt.routing.model_router import load_registry, tier_for_model

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
    result = score.value
    _cuv_cache[cache_key] = result
    return result
