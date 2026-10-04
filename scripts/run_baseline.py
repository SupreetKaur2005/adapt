"""Entry point: runs `baseline.baseline_llm`/`baseline.baseline_scanner` instead
of the full system.
"""
from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an A.D.A.P.T. baseline comparison.")
    parser.add_argument("--mode", choices=["llm", "scanner"], default="llm")
    parser.parse_args()
    raise NotImplementedError


if __name__ == "__main__":
    main()
