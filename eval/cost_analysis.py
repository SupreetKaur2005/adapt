"""Computes actual cost deltas from `adapt.utils.metrics` output across the
three conditions. This is the file that produces the 60-80% cost-savings
number -- without running it, that figure is a target, not a result.
"""
from __future__ import annotations


def compute_cost_delta(routed_metrics: dict, baseline_metrics: dict) -> float:
    raise NotImplementedError
