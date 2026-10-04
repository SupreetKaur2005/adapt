from __future__ import annotations

import tempfile
from pathlib import Path

from eval.cost_analysis import compute_cost_delta
from eval.results_dashboard import render_dashboard
from eval.run_comparison import run_comparison


def test_compute_cost_delta():
    routed = {"cumulative_cost": 25.0}
    baseline = {"cumulative_cost": 100.0}
    savings = compute_cost_delta(routed, baseline)
    assert savings == 75.0


def test_render_dashboard():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = Path(tmpdir) / "dashboard.html"
        results = {
            "routed": {"cumulative_cost": 0.02, "verdicts": {"PASS": 2}},
            "baseline": {"cumulative_cost": 0.08, "verdicts": {"PASS": 2}},
            "cost_savings_pct": 75.0,
        }
        html = render_dashboard(results, out_file)
        assert out_file.exists()
        assert "75.0%" in html
        assert "A.D.A.P.T. Simulation Results" in html


def test_run_comparison():
    res = run_comparison(n_rounds=1)
    assert "cost_savings_pct" in res
    assert res["cost_savings_pct"] == 75.0
