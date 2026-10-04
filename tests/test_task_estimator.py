"""Tests for `adapt.routing.task_estimator`."""
from adapt.routing.task_estimator import DEFAULT_COLD_START, estimate
from adapt.schemas import AttackTechnique


def test_cold_start_known_tactic():
    from adapt.memory.csim_store import clear
    clear()
    technique = AttackTechnique(
        technique_id="T1558", name="Kerberoasting", tactic="credential-access"
    )
    success_rate, stealth = estimate("roast a ticket", technique)
    assert (success_rate, stealth) == (0.5, 0.7)


def test_cold_start_unknown_tactic_uses_default():
    from adapt.memory.csim_store import clear
    clear()
    technique = AttackTechnique(technique_id="T9999", name="made up", tactic="nonexistent")
    assert estimate("do something novel", technique) == DEFAULT_COLD_START


def test_warm_start_uses_csim():
    from adapt.memory.csim_store import clear, commit
    from adapt.schemas import ExploitAttempt

    clear()
    tech = AttackTechnique(technique_id="T1558", name="Kerberoasting", tactic="credential-access")
    exploit = ExploitAttempt(
        subtask="kerberoast the domain controller",
        technique=tech,
        payload="kerberoast payload",
        model_used="mistral:7b",
    )
    commit(exploit, {"patch": "diff"})

    success_rate, stealth = estimate("kerberoast the domain controller", tech)
    assert success_rate == 1.0
    assert stealth == 0.6
