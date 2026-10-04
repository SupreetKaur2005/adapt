"""Harness that runs A.D.A.P.T. against the NYU CTF Bench task set."""
from __future__ import annotations

from adapt.orchestrator import Orchestrator
from adapt.schemas import FrozenConstraints, RevisableStrategy, RoEContract


def run_nyu_ctf(challenge_name: str = "nyu-ctf-auth-bypass", n_rounds: int = 2) -> dict:
    """Run A.D.A.P.T. against NYU CTF Bench challenge."""
    contract = RoEContract(
        frozen_constraints=FrozenConstraints(
            intent=f"NYU CTF Bench: {challenge_name}",
            max_execution_time_s=180,
        ),
        revisable_strategy=RevisableStrategy(
            objective=f"Capture flag for challenge {challenge_name}",
            verification_criteria=["flag_submitted"],
        ),
    )
    orch = Orchestrator(contract=contract)
    state = orch.run_episode(n_rounds=n_rounds)
    return {
        "benchmark": "NYU CTF Bench",
        "challenge": challenge_name,
        "rounds_completed": state.round_number,
        "verdicts": state.verdicts,
        "solved": "PASS" in state.verdicts,
    }
