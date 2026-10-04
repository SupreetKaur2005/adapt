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
    print(f"Starting A.D.A.P.T. simulation for up to {n_rounds} rounds...")
    orch = Orchestrator(contract=contract, model_client=model_client)
    state = orch.run_episode(n_rounds=n_rounds)
    
    print(f"\nSimulation completed {state.round_number} rounds. Verdicts: {state.verdicts}")
    
    passes = state.verdicts.count('PASS')
    blocks = state.verdicts.count('BLOCK')
    pivots = state.verdicts.count('PIVOT')
    
    report_lines = []
    report_lines.append("# A.D.A.P.T. Detailed End-of-Episode Report\n")
    report_lines.append("## High-Level Stats")
    report_lines.append(f"- **Total Rounds Executed:** {state.round_number} (out of {n_rounds} max)")
    report_lines.append(f"- **Successful Exploits (PASS):** {passes}")
    report_lines.append(f"- **Blocked/Patched (BLOCK):** {blocks}")
    report_lines.append(f"- **Attack Pivots (PIVOT):** {pivots}\n")
    
    report_lines.append("## Round-by-Round Breakdown\n")
    for record in state.history:
        r = record.get('round', '?')
        v = record.get('verdict', 'UNKNOWN')
        report_lines.append(f"### Round {r} -> {v}")
        
        red = record.get('red_outcome', {})
        if red.get('success'):
            report_lines.append("- 🔴 **Red Team Action:** Generated successful exploit payload.")
        elif red.get('contract_violation'):
            report_lines.append(f"- 🔴 **Red Team Blocked:** {red.get('reason')}")
            
        blue = record.get('blue_outcome', {})
        if blue:
            patch = blue.get('patch', {})
            if patch.get('file_path'):
                report_lines.append(f"- 🔵 **Blue Team Defense:** Synthesized patch for `{patch.get('file_path')}`")
            if blue.get('yara'):
                report_lines.append("- 🔵 **Blue Team Defense:** Deployed YARA detection rule.")
                
        report_lines.append(f"- ⚖️ **Triage Reason:** {record.get('reason', 'N/A')}\n")
    
    report_path = Path("simulation_report.md")
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"\n[+] Detailed report saved to {report_path.absolute()}")
    
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an A.D.A.P.T. simulation episode.")
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--objective", type=str, default="discover kerberos services and patch tickets")
    args = parser.parse_args()
    sys.exit(run_simulation(n_rounds=args.rounds, objective=args.objective))


if __name__ == "__main__":
    main()
