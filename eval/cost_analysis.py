"""Computes actual cost deltas from `adapt.utils.metrics` output across conditions.
This produces the 60-80% cost-savings metric.
"""
from __future__ import annotations


def compute_cost_delta(routed_metrics: dict, baseline_metrics: dict) -> float:
    """Calculate the percentage cost reduction of routed vs monolithic baseline.

    Returns percentage savings (e.g. 72.5 means 72.5% savings).
    """
    routed_cost = float(routed_metrics.get("cumulative_cost", 0.0))
    baseline_cost = float(baseline_metrics.get("cumulative_cost", 0.0))

    if baseline_cost <= 0.0:
        return 0.0

    savings = (baseline_cost - routed_cost) / baseline_cost * 100.0
    return round(savings, 2)
