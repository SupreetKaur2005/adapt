"""Tracks running counts: PASS/BLOCK/PIVOT rate, per-round model cost,
cumulative cost vs. the baseline. Feeds `eval.cost_analysis`.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field


@dataclass
class Metrics:
    verdict_counts: Counter = field(default_factory=Counter)
    cumulative_cost: float = 0.0

    def record_verdict(self, verdict: str) -> None:
        self.verdict_counts[verdict] += 1

    def record_cost(self, cost: float) -> None:
        self.cumulative_cost += cost
