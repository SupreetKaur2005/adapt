"""Tests for `adapt.agents.red_team.payload_mutator`."""
from adapt.agents.red_team.payload_mutator import mutate
from adapt.schemas import AttackTechnique, ExploitAttempt


def _exploit() -> ExploitAttempt:
    technique = AttackTechnique(
        technique_id="T1558", name="Kerberoasting", tactic="credential-access"
    )
    return ExploitAttempt(
        subtask="roast a ticket", technique=technique, payload="original payload",
        model_used="mistral:7b",
    )


def test_mutate_falls_back_to_naive_mutation_when_no_playbooks():
    # datasets.atomic_redteam_loader.load_playbooks isn't implemented yet,
    # so this exercises the graceful cold-start-style fallback path.
    mutated = mutate(_exploit(), "T1558")

    assert mutated.payload.startswith("original payload")
    assert "mutated-variant" in mutated.payload
    assert mutated.model_used == "mistral:7b"
    assert mutated.subtask == "roast a ticket"
