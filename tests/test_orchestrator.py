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
