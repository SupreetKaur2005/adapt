"""Tests for `adapt.routing.task_estimator`."""
from adapt.routing.task_estimator import DEFAULT_COLD_START, estimate
from adapt.schemas import AttackTechnique


def test_cold_start_known_tactic():
    technique = AttackTechnique(
        technique_id="T1558", name="Kerberoasting", tactic="credential-access"
    )
    success_rate, stealth = estimate("roast a ticket", technique)
    assert (success_rate, stealth) == (0.5, 0.7)


def test_cold_start_unknown_tactic_uses_default():
    technique = AttackTechnique(technique_id="T9999", name="made up", tactic="nonexistent")
    assert estimate("do something novel", technique) == DEFAULT_COLD_START
