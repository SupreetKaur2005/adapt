"""Entry point: builds the sandbox, runs `orchestrator.run_episode()` for N rounds."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Ensure project root and src/ are on sys.path for direct CLI execution
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from adapt.orchestrator import Orchestrator
from adapt.schemas import FrozenConstraints, RevisableStrategy, RoEContract


def run_simulation(
    n_rounds: int = 5,
    objective: str = "discover kerberos services and patch tickets",
    model_client: object = None,
) -> int:
    contract = RoEContract(
        frozen_constraints=FrozenConstraints(
            intent="Live simulation run",
            max_execution_time_s=180,
        ),
        revisable_strategy=RevisableStrategy(
            objective=objective,
            verification_criteria=["remediation_verified"],
        ),
    )
    print(f"Starting A.D.A.P.T. simulation for {n_rounds} rounds...")
    orch = Orchestrator(contract=contract, model_client=model_client)
    state = orch.run_episode(n_rounds=n_rounds)
    print(f"Simulation completed {state.round_number} rounds. Verdicts: {state.verdicts}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an A.D.A.P.T. simulation episode.")
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--objective", type=str, default="discover kerberos services and patch tickets")
    args = parser.parse_args()
    sys.exit(run_simulation(n_rounds=args.rounds, objective=args.objective))


if __name__ == "__main__":
    main()
