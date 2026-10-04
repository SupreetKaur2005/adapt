"""Wraps a traditional (non-agentic) vulnerability scanner over the same
sandbox targets, for the "does an agentic approach even help" comparison.
"""
from __future__ import annotations


def run_baseline_scanner(target_host: str) -> dict:
    raise NotImplementedError
