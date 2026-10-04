from __future__ import annotations

from unittest.mock import MagicMock

from adapt.orchestrator import Orchestrator
from adapt.schemas import FrozenConstraints, RevisableStrategy, RoEContract


def test_orchestrator_run_episode_passes():
    contract = RoEContract(
        frozen_constraints=FrozenConstraints(
            intent="Test automated defense loop",
            prohibited_subnets=["192.168.100.0/24"],
            max_execution_time_s=60,
        ),
        revisable_strategy=RevisableStrategy(
            objective="discover kerberos services and patch tickets",
            verification_criteria=["remediation_verified"],
        ),
    )

    mock_client = MagicMock()
    mock_client.generate.return_value = "File: fix.py\nDescription: fix\n```diff\n+fixed\n```"

    orch = Orchestrator(contract=contract, model_client=mock_client)
    final_state = orch.run_episode(n_rounds=2)

    assert final_state.round_number == 2
    assert len(final_state.history) == 2
    assert len(final_state.verdicts) == 2
    assert final_state.history[0]["round"] == 1
    assert final_state.history[1]["round"] == 2
    assert all(v == "PASS" for v in final_state.verdicts)


def test_orchestrator_blocked_path_on_roe_violation(monkeypatch):
    from adapt.sandbox import container_manager

    resets = []
    monkeypatch.setattr(container_manager, "reset", lambda: resets.append(True))

    contract = RoEContract(
        frozen_constraints=FrozenConstraints(
            intent="Test RoE constraint enforcement",
            prohibited_subnets=["10.10.0.0/16"],
            max_execution_time_s=60,
        ),
        revisable_strategy=RevisableStrategy(
            objective="test exploit against prohibited host",
            verification_criteria=["remediation_verified"],
        ),
    )

    mock_client = MagicMock()
    orch = Orchestrator(
        contract=contract,
        model_client=mock_client,
        target_host="10.10.1.5",
    )
    final_state = orch.run_episode(n_rounds=3)

    # Execution should immediately terminate on BLOCK in round 1
    assert len(final_state.verdicts) == 1
    assert final_state.verdicts[0] == "BLOCK"
    assert len(final_state.history) == 1
    assert final_state.history[0]["red_outcome"]["contract_violation"] is True
    assert final_state.history[0]["blue_outcome"] == {}
    assert len(resets) >= 1


def test_orchestrator_pivot_path_and_mutation():
    contract = RoEContract(
        frozen_constraints=FrozenConstraints(
            intent="Test pivot path with payload mutation",
            prohibited_subnets=["192.168.100.0/24"],
            max_execution_time_s=60,
        ),
        revisable_strategy=RevisableStrategy(
            objective="discover kerberos services and patch tickets",
            verification_criteria=["remediation_verified"],
        ),
    )

    mock_client = MagicMock()
    mock_client.generate.return_value = "File: fix.py\nDescription: fix\n```diff\n+fixed\n```"

    # verify_remediation=False forces blue outcome to fail verification -> PIVOT
    orch = Orchestrator(
        contract=contract,
        model_client=mock_client,
        verify_remediation=False,
    )
    final_state = orch.run_episode(n_rounds=2)

    assert len(final_state.verdicts) == 2
    assert final_state.verdicts[0] == "PIVOT"
    # Round 2 executed under PIVOT mode
    assert final_state.history[1]["round"] == 2


def test_orchestrator_builds_and_wires_graphs():
    from adapt.orchestrator import build_graph_bundle

    sample_src = """
def test_fn(x):
    y = x + 1
    return y
"""
    graphs = build_graph_bundle(sample_src)
    assert "ast" in graphs
    assert "cfg" in graphs
    assert "dfg" in graphs
    assert "pdg" in graphs
    assert len(graphs["cfg"].nodes) > 0
    assert len(graphs["dfg"].nodes) > 0
    assert len(graphs["pdg"].nodes) > 0
