from __future__ import annotations

from unittest.mock import MagicMock

from baseline.baseline_llm import run_baseline_llm
from baseline.baseline_scanner import run_baseline_scanner
from baseline.cybench_adapter import run_cybench
from baseline.nyu_ctf_adapter import run_nyu_ctf
from scripts.run_baseline import run_baseline
from scripts.run_simulation import run_simulation


def test_baseline_llm():
    mock_client = MagicMock()
    mock_client.generate.return_value = "Plan step 1, 2, 3"
    res = run_baseline_llm("test exploit target", model_client=mock_client)
    assert res["model"] == "deepseek-coder:33b"
    assert "Plan step" in res["response"]
    assert res["estimated_cost"] > 0


def test_baseline_scanner():
    res = run_baseline_scanner("127.0.0.1", ports=[80, 445])
    assert res["target_host"] == "127.0.0.1"
    assert "findings" in res


def test_cybench_adapter():
    res = run_cybench(task_id="cybench-test", n_rounds=1)
    assert res["benchmark"] == "Cybench"
    assert res["rounds_completed"] == 1


def test_nyu_ctf_adapter():
    res = run_nyu_ctf(challenge_name="test-challenge", n_rounds=1)
    assert res["benchmark"] == "NYU CTF Bench"
    assert res["rounds_completed"] == 1


def test_scripts_run_baseline_scanner():
    res = run_baseline(mode="scanner", target="127.0.0.1", n_rounds=2, ports=[80, 445])
    assert res["rounds_completed"] == 2
    assert res["mode"] == "scanner"
    assert "scanner" in res["round_summaries"][0]


def test_scripts_run_baseline_llm(mock_ollama_client):
    res = run_baseline(mode="llm", target="127.0.0.1", n_rounds=1, model_client=mock_ollama_client)
    assert res["rounds_completed"] == 1
    assert res["mode"] == "llm"
    assert "llm" in res["round_summaries"][0]
    assert res["total_cost"] >= 0


def test_scripts_run_baseline_both(mock_ollama_client):
    res = run_baseline(mode="both", target="127.0.0.1", n_rounds=1, model_client=mock_ollama_client)
    assert res["rounds_completed"] == 1
    assert "scanner" in res["round_summaries"][0]
    assert "llm" in res["round_summaries"][0]


def test_scripts_run_simulation(mock_ollama_client):
    code = run_simulation(n_rounds=1, model_client=mock_ollama_client)
    assert code == 0
