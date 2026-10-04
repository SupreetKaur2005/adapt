"""Apply the RoE and issue a PASS, BLOCK, or PIVOT verdict."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from adapt.schemas import ExploitAttempt, RoEContract, TriageOutcome, Verdict


def _flag(outcome: Mapping[str, Any], *keys: str) -> bool:
    for key in keys:
        value = outcome.get(key)
        if value is True or (isinstance(value, str) and value.strip().lower() in {"true", "yes", "success", "succeeded", "passed", "blocked"}):
            return True
    return False


def _round_number(*outcomes: Mapping[str, Any]) -> int:
    for outcome in outcomes:
        value = outcome.get("round_number")
        if isinstance(value, int) and value > 0:
            return value
    return 1


def _criteria_satisfied(blue_outcome: Mapping[str, Any], contract: RoEContract) -> bool:
    criteria = contract.revisable_strategy.verification_criteria
    if not criteria:
        return True
    if _flag(blue_outcome, "verification_passed", "criteria_met"):
        return True
    results = blue_outcome.get("criteria_results")
    if isinstance(results, Mapping):
        return all(results.get(item) is True for item in criteria)
    verified = blue_outcome.get("verified_criteria")
    if isinstance(verified, (list, tuple, set)):
        confirmed = {str(item).strip().casefold() for item in verified}
        return all(item.strip().casefold() in confirmed for item in criteria)
    return False


def _block(reason: str, action: dict[str, Any], round_number: int) -> TriageOutcome:
    from adapt.audit.audit_log import record
    from adapt.sandbox.container_manager import reset

    record(action, reason)
    reset()
    return TriageOutcome(verdict=Verdict.BLOCK, reason=reason, round_number=round_number)


def triage(red_outcome: dict, blue_outcome: dict, contract: RoEContract) -> TriageOutcome:
    """Arbitrate the round against the contract.

    A contract violation always blocks and resets the sandbox. PASS requires
    verified success from both teams; any unresolved or incomplete result asks
    Red to pivot. A passing exploit/patch pair is added to the CSIM registry
    when both typed artifacts are provided.
    """
    if not isinstance(red_outcome, dict) or not isinstance(blue_outcome, dict):
        raise TypeError("red_outcome and blue_outcome must be dictionaries")
    if not isinstance(contract, RoEContract):
        raise TypeError("contract must be a RoEContract")
    round_number = _round_number(red_outcome, blue_outcome)

    # Recheck proposed Red actions at the arbiter boundary so an upstream
    # enforcement omission cannot turn a prohibited action into a PASS.
    from adapt.contract.constraint_enforcer import check

    for team, outcome in (("red", red_outcome), ("blue", blue_outcome)):
        actions = outcome.get("actions", [])
        if not isinstance(actions, list):
            continue
        for action in actions:
            if isinstance(action, dict):
                result = check(action, contract)
                if not result.allowed:
                    from adapt.sandbox.container_manager import reset

                    reset()
                    return TriageOutcome(
                        verdict=Verdict.BLOCK,
                        reason=f"{team} action: {result.reason}",
                        round_number=round_number,
                    )

    if _flag(red_outcome, "contract_violation", "blocked", "roe_violation"):
        reason = str(red_outcome.get("reason") or "Red action was blocked by the Rules of Engagement")
        blocked_action = red_outcome.get("blocked_action")
        if not isinstance(blocked_action, dict):
            blocked_action = {"team": "red", "reason": reason}
        return _block(reason, blocked_action, round_number)

    red_ok = _flag(red_outcome, "success", "succeeded", "verified", "red_succeeded")
    blue_ok = _flag(blue_outcome, "success", "succeeded", "verified", "blue_succeeded")
    if red_ok and blue_ok and _criteria_satisfied(blue_outcome, contract):
        exploit = red_outcome.get("exploit") or red_outcome.get("exploit_attempt")
        patch = blue_outcome.get("patch")
        if isinstance(exploit, ExploitAttempt) and isinstance(patch, dict):
            from adapt.memory.csim_store import commit

            commit(exploit, patch)
        return TriageOutcome(verdict=Verdict.PASS, reason="Red success and Blue remediation were verified", round_number=round_number)

    return TriageOutcome(
        verdict=Verdict.PIVOT,
        reason="Round did not verify both the Red outcome and the Blue response",
        round_number=round_number,
    )
