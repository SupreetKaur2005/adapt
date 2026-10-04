"""Tests for `adapt.agents.red_team.payload_mutator`."""
from unittest.mock import MagicMock

from adapt.agents.red_team.payload_mutator import mutate
from adapt.schemas import AttackTechnique, ExploitAttempt


def _exploit() -> ExploitAttempt:
    technique = AttackTechnique(
        technique_id="T1558", name="Kerberoasting", tactic="credential-access"
    )
    return ExploitAttempt(
        subtask="roast a ticket",
        technique=technique,
        payload="original payload",
        model_used="mistral:7b",
    )


def test_mutate_falls_back_to_naive_mutation_when_no_playbooks():
    # When no playbooks exist for technique (e.g. unknown technique T9999),
    # fallback to deterministic naive mutation
    mutated = mutate(_exploit(), "T9999")

    assert mutated.payload.startswith("original payload")
    assert "mutated-variant" in mutated.payload
    assert mutated.model_used == "mistral:7b"
    assert mutated.subtask == "roast a ticket"


def test_mutate_with_atomic_seed():
    # For supported techniques, mutator uses Atomic Red Team seeds via model client
    mock_client = MagicMock()
    mock_client.generate.return_value = "mutated_seed_payload"

    mutated = mutate(_exploit(), "T1558", model_client=mock_client)
    assert mutated.payload == "mutated_seed_payload"
    mock_client.generate.assert_called_once()
