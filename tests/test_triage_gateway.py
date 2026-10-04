"""Tests for the RoE triage arbiter."""
from adapt.schemas import AttackTechnique, ExploitAttempt, FrozenConstraints, RevisableStrategy, RoEContract, Verdict
from adapt.verification.triage_gateway import triage


def contract() -> RoEContract:
    return RoEContract(
        frozen_constraints=FrozenConstraints(intent="authorized lab", max_execution_time_s=60),
        revisable_strategy=RevisableStrategy(objective="test detection", verification_criteria=["patch verified"]),
    )


def test_triage_passes_only_when_both_outcomes_are_verified():
    result = triage(
        {"success": True, "round_number": 4},
        {"success": True, "verified_criteria": ["patch verified"]},
        contract(),
    )
    assert result.verdict is Verdict.PASS
    assert result.round_number == 4


def test_triage_pivots_when_outcome_is_incomplete():
    result = triage({"success": True}, {"success": False}, contract())
    assert result.verdict is Verdict.PIVOT


def test_triage_commits_verified_exploit_patch_pair(monkeypatch):
    from adapt.memory import csim_store

    committed = []
    monkeypatch.setattr(csim_store, "commit", lambda exploit, patch: committed.append((exploit, patch)))
    exploit = ExploitAttempt(
        subtask="verify service discovery",
        technique=AttackTechnique(technique_id="T1046", name="Network Service Discovery", tactic="discovery"),
        payload="authorized test payload",
        model_used="local-test-model",
    )
    patch = {"file_path": "service.py", "diff": "test", "description": "mitigation"}

    result = triage(
        {"success": True, "exploit": exploit},
        {"success": True, "patch": patch, "verified_criteria": ["patch verified"]},
        contract(),
    )
    assert result.verdict is Verdict.PASS
    assert committed == [(exploit, patch)]


def test_contract_violation_blocks_audits_and_resets(monkeypatch):
    from adapt.audit import audit_log
    from adapt.sandbox import container_manager

    recorded = []
    reset_calls = []
    monkeypatch.setattr(audit_log, "record", lambda action, reason: recorded.append((action, reason)))
    monkeypatch.setattr(container_manager, "reset", lambda: reset_calls.append(True))
    result = triage(
        {"actions": [{"tool": "port_scan", "target_host": "10.0.0.5"}]},
        {},
        RoEContract(
            frozen_constraints=FrozenConstraints(
                intent="authorized lab", prohibited_subnets=["10.0.0.0/24"], max_execution_time_s=60
            ),
            revisable_strategy=RevisableStrategy(objective="test", verification_criteria=[]),
        ),
    )
    assert result.verdict is Verdict.BLOCK
    assert recorded and "prohibited subnet" in recorded[0][1]
    assert reset_calls == [True]
