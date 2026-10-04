"""Harness that runs A.D.A.P.T. against the Cybench task set."""
from __future__ import annotations

from adapt.orchestrator import Orchestrator
from adapt.schemas import FrozenConstraints, RevisableStrategy, RoEContract


def run_cybench(task_id: str = "cybench-kerberos-01", n_rounds: int = 2) -> dict:
    """Run A.D.A.P.T. agentic loop against a Cybench benchmark task."""
    contract = RoEContract(
        frozen_constraints=FrozenConstraints(
            intent=f"Cybench Benchmark: {task_id}",
            max_execution_time_s=180,
        ),
        revisable_strategy=RevisableStrategy(
            objective=f"Solve benchmark task {task_id}",
            verification_criteria=["flag_captured", "patch_verified"],
        ),
    )
    orch = Orchestrator(contract=contract)
    state = orch.run_episode(n_rounds=n_rounds)
    return {
        "benchmark": "Cybench",
        "task_id": task_id,
        "rounds_completed": state.round_number,
        "verdicts": state.verdicts,
        "success": "PASS" in state.verdicts,
    }
