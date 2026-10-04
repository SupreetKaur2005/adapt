from __future__ import annotations

from adapt.utils.metrics import Metrics


def test_metrics_recording():
    metrics = Metrics()
    assert metrics.cumulative_cost == 0.0
    assert len(metrics.verdict_counts) == 0

    metrics.record_verdict("PASS")
    metrics.record_verdict("PASS")
    metrics.record_verdict("BLOCK")
    metrics.record_cost(0.015)
    metrics.record_cost(0.005)

    assert metrics.verdict_counts["PASS"] == 2
    assert metrics.verdict_counts["BLOCK"] == 1
    assert round(metrics.cumulative_cost, 4) == 0.02
