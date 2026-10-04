"""A deliberately simple comparison system: one frontier-equivalent local
model handling every subtask, no CUV routing, no tiering. Used to measure
what routing actually saves.
"""
from __future__ import annotations


def run_baseline_llm(subtask: str) -> dict:
    raise NotImplementedError
