"""Generates HTML dashboard summarizing PASS/BLOCK/PIVOT rates and cost comparison."""
from __future__ import annotations

from pathlib import Path


def render_dashboard(results: dict, output_path: str | Path) -> str:
    """Renders a self-contained HTML dashboard of simulation results."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    routed = results.get("routed", {})
    baseline = results.get("baseline", {})
    savings = results.get("cost_savings_pct", 0.0)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>A.D.A.P.T. Evaluation Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; background: #0f172a; color: #f8fafc; }}
        .card {{ background: #1e293b; padding: 24px; border-radius: 12px; margin-bottom: 24px; border: 1px solid #334155; }}
        h1 {{ color: #38bdf8; margin-top: 0; }}
        .metric {{ font-size: 32px; font-weight: bold; color: #4ade80; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
        th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #334155; }}
        th {{ color: #94a3b8; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>A.D.A.P.T. Simulation Results</h1>
        <p>Cost Savings vs Monolithic Baseline:</p>
        <div class="metric">{savings}%</div>
    </div>
    <div class="card">
        <h2>Performance Comparison</h2>
        <table>
            <tr><th>Metric</th><th>Routed (TOPAZ)</th><th>Monolithic Baseline</th></tr>
            <tr><td>Total Cost</td><td>${routed.get("cumulative_cost", 0.0):.4f}</td><td>${baseline.get("cumulative_cost", 0.0):.4f}</td></tr>
            <tr><td>PASS Count</td><td>{routed.get("verdicts", {}).get("PASS", 0)}</td><td>{baseline.get("verdicts", {}).get("PASS", 0)}</td></tr>
            <tr><td>BLOCK Count</td><td>{routed.get("verdicts", {}).get("BLOCK", 0)}</td><td>{baseline.get("verdicts", {}).get("BLOCK", 0)}</td></tr>
            <tr><td>PIVOT Count</td><td>{routed.get("verdicts", {}).get("PIVOT", 0)}</td><td>{baseline.get("verdicts", {}).get("PIVOT", 0)}</td></tr>
        </table>
    </div>
</body>
</html>"""
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return html
