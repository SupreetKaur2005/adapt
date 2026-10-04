"""The single enforcement point (v2 had this duplicated across two files --
fixed here).
"""
from __future__ import annotations

import ipaddress
from dataclasses import dataclass

from adapt.schemas import RoEContract


@dataclass
class EnforcementResult:
    allowed: bool
    reason: str = ""

    @classmethod
    def ok(cls) -> "EnforcementResult":
        return cls(allowed=True)

    @classmethod
    def blocked(cls, reason: str) -> "EnforcementResult":
        return cls(allowed=False, reason=reason)


def _host_is_prohibited(target_host: str, prohibited_subnets: list[str]) -> bool:
    try:
        host_ip = ipaddress.ip_address(target_host)
    except ValueError:
        host_ip = None

    for entry in prohibited_subnets:
        if host_ip is not None:
            try:
                if host_ip in ipaddress.ip_network(entry, strict=False):
                    return True
                continue
            except ValueError:
                pass
        if target_host == entry:
            return True
    return False


def check(action: dict, contract: RoEContract) -> EnforcementResult:
    """Check an action against the contract. On BLOCKED, writes to adapt.audit.audit_log."""
    from adapt.audit.audit_log import record

    frozen = contract.frozen_constraints

    target_host = action.get("target_host")
    if target_host and _host_is_prohibited(target_host, frozen.prohibited_subnets):
        reason = f"target_host '{target_host}' is in a prohibited subnet"
        record(action, reason)
        return EnforcementResult.blocked(reason)

    tool = action.get("tool", "")
    if tool:
        for rule in frozen.absolute_rules:
            if tool.lower() in rule.lower():
                reason = f"violates absolute rule: {rule!r}"
                record(action, reason)
                return EnforcementResult.blocked(reason)

    elapsed = action.get("elapsed_time_s", 0)
    if elapsed > frozen.max_execution_time_s:
        reason = (
            f"elapsed_time_s={elapsed} exceeds max_execution_time_s="
            f"{frozen.max_execution_time_s}"
        )
        record(action, reason)
        return EnforcementResult.blocked(reason)

    return EnforcementResult.ok()
