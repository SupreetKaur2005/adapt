"""Entry point: runs `baseline.baseline_llm`/`baseline.baseline_scanner` instead
of the full system.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

# Ensure project root and src/ are on sys.path for direct CLI execution
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from baseline.baseline_llm import run_baseline_llm
from baseline.baseline_scanner import run_baseline_scanner


def run_baseline(
    mode: str = "llm",
    target: str = "127.0.0.1",
    n_rounds: int = 5,
    objective: str = "discover kerberos services and patch tickets",
    model_client: object = None,
    ports: list[int] | None = None,
) -> dict:
    """Run baseline LLM or scanner across N rounds to compare against full A.D.A.P.T. system."""
    print(f"Starting A.D.A.P.T. baseline ({mode}) against {target} for {n_rounds} rounds...")
    total_tokens = 0
    total_cost = 0.0
    all_findings = []
    round_summaries = []

    for r in range(1, n_rounds + 1):
        round_info: dict[str, Any] = {"round": r}
        if mode in ("scanner", "both"):
            scanner_res = run_baseline_scanner(target, ports=ports)
            round_info["scanner"] = scanner_res
            all_findings.extend(scanner_res.get("findings", []))
            print(f"  [Round {r}] Baseline Scanner findings on {target}: {scanner_res['findings_count']}")

        if mode in ("llm", "both"):
            subtask_prompt = f"Round {r}/{n_rounds}: {objective} on target {target}"
            llm_res = run_baseline_llm(subtask_prompt, model_client=model_client)
            round_info["llm"] = llm_res
            total_tokens += llm_res.get("estimated_tokens", 0)
            total_cost += llm_res.get("estimated_cost", 0.0)
            print(
                f"  [Round {r}] Baseline Heavy LLM ({llm_res.get('model')}): "
                f"tokens={llm_res.get('estimated_tokens')}, cost=${llm_res.get('estimated_cost'):.4f}"
            )

        round_summaries.append(round_info)

    summary = {
        "mode": mode,
        "target": target,
        "rounds_completed": n_rounds,
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 6),
        "total_findings": len(all_findings),
        "round_summaries": round_summaries,
    }
    print(
        f"Baseline completed {n_rounds} rounds. Mode={mode}. "
        f"Total Cost: ${summary['total_cost']:.4f} | Total Tokens: {summary['total_tokens']} | Findings: {summary['total_findings']}"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an A.D.A.P.T. baseline comparison.")
    parser.add_argument("--mode", choices=["llm", "scanner", "both"], default="llm")
    parser.add_argument("--target", type=str, default="127.0.0.1")
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--objective", type=str, default="discover kerberos services and patch tickets")
    parser.add_argument("--ports", nargs="*", type=int, default=None, help="Target ports to scan")
    args = parser.parse_args()
    run_baseline(
        mode=args.mode,
        target=args.target,
        n_rounds=args.rounds,
        objective=args.objective,
        ports=args.ports,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
