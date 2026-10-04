"""Entry point: builds the sandbox, runs `orchestrator.run_episode()` for N rounds."""
from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an A.D.A.P.T. simulation episode.")
    parser.add_argument("--rounds", type=int, default=10)
    parser.parse_args()
    raise NotImplementedError


if __name__ == "__main__":
    main()
