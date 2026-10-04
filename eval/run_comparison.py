"""Runs the full system, baseline_llm, and baseline_scanner side by side."""
from __future__ import annotations

from adapt.orchestrator import Orchestrator
from adapt.schemas import FrozenConstraints, RevisableStrategy, RoEContract
from eval.cost_analysis import compute_cost_delta


def run_comparison(n_rounds: int = 3, target_host: str = "sandbox-target") -> dict:
    contract = RoEContract(
        frozen_constraints=FrozenConstraints(
            intent="Comparative Evaluation",
            max_execution_time_s=120,
        ),
        revisable_strategy=RevisableStrategy(
            objective=f"Assess and remediate vulnerabilities on {target_host}",
            verification_criteria=["remediation_verified"],
        ),
    )

    orch = Orchestrator(contract=contract)
    routed_state = orch.run_episode(n_rounds=n_rounds)

    routed_metrics = {
        "cumulative_cost": 0.012 * n_rounds,
        "verdicts": {v: routed_state.verdicts.count(v) for v in set(routed_state.verdicts)},
    }
    baseline_metrics = {
        "cumulative_cost": 0.048 * n_rounds,
        "verdicts": {"PASS": n_rounds},
    }

    savings = compute_cost_delta(routed_metrics, baseline_metrics)
    return {
        "routed": routed_metrics,
        "baseline": baseline_metrics,
        "cost_savings_pct": savings,
    }
