#!/usr/bin/env python3
"""CLI entry point for A.D.A.P.T. single‑repo simulation.

Usage:
    python -m adapt.scan_cli --repo <git-url> [--rounds N]

The script clones the repo, collects Python source files, runs a single‑round
A.D.A.P.T. episode and prints an executive summary.
"""
from __future__ import annotations

import sys
import os
import shutil
import tempfile
import subprocess
import glob

# Ensure the project source is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from adapt.orchestrator import Orchestrator
from adapt.routing.model_clients.ollama_client import OllamaClient


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: adapt scan --repo <git-url> [--rounds N]")
        sys.exit(1)

    repo_url = None
    rounds = 3
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--repo" and i + 1 < len(args):
            repo_url = args[i + 1]
            i += 2
        elif args[i] == "--rounds" and i + 1 < len(args):
            rounds = int(args[i + 1])
            i += 2
        else:
            i += 1

    if not repo_url:
        print("Error: --repo <git-url> is required.")
        sys.exit(1)

    # Check for Ollama
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/", timeout=1.0)
        model_client = OllamaClient()
    except Exception:
        model_client = OllamaClient()

    # Clone the repository
    tmp_dir = tempfile.mkdtemp()
    try:
        subprocess.run(["git", "clone", repo_url, tmp_dir], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Git clone failed: {e.stderr.decode()}")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        sys.exit(1)

    # Collect Python source files (mirrors UI logic)
    target_code_parts: list[str] = []
    for file in glob.glob(os.path.join(tmp_dir, "**", "*.py"), recursive=True):
        try:
            with open(file, "r", encoding="utf-8") as f:
                target_code_parts.append("# --- " + os.path.basename(file) + " ---\n" + f.read())
        except Exception:
            pass

    target_code = "\n".join(target_code_parts) if target_code_parts else "def authenticate(username, password):\n    pass"

    orch = Orchestrator(target_code=target_code, model_client=model_client)
    state = orch.run_episode(n_rounds=rounds)

    tested = len(state.history)
    passed = sum(1 for h in state.history if h.get("verdict") == "PASS")
    blocked = sum(1 for h in state.history if h.get("verdict") == "BLOCK")
    pivot = sum(1 for h in state.history if h.get("verdict") == "PIVOT")
    score = int((blocked / max(tested, 1)) * 100) if tested else 0

    print("\n=== Simulation Results ===")
    print(f"Rounds: {rounds}")
    print(f"Techniques tested: {tested}")
    print(f"PASS: {passed}, BLOCK: {blocked}, PIVOT: {pivot}")
    print(f"Estimated cost score: {score}%")
    print(f"Remediations: {state.remediations}")

    shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()