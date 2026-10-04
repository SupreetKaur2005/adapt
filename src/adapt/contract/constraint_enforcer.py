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


def _extract_host(raw_host: str) -> str:
    host = raw_host.strip()
    if "://" in host:
        host = host.split("://", 1)[1].split("/")[0]
    if host.startswith("[") and "]" in host:
        host = host[1:host.index("]")]
    elif ":" in host and host.count(":") == 1:
        host = host.split(":", 1)[0]
    return host


def _host_is_prohibited(target_host: str, prohibited_subnets: list[str]) -> bool:
    if not isinstance(target_host, str) or not target_host.strip():
        return False

    clean_host = _extract_host(target_host)
    try:
        host_ip = ipaddress.ip_address(clean_host)
    except ValueError:
        host_ip = None

    for entry in prohibited_subnets:
        if not isinstance(entry, str) or not entry.strip():
            continue
        entry_stripped = entry.strip()
        if host_ip is not None:
            try:
                if host_ip in ipaddress.ip_network(entry_stripped, strict=False):
                    return True
                continue
            except ValueError:
                pass
        if clean_host.lower() == entry_stripped.lower() or target_host.strip().lower() == entry_stripped.lower():
            return True
    return False


def check(action: dict, contract: RoEContract) -> EnforcementResult:
    """Check an action against the contract. On BLOCKED, writes to adapt.audit.audit_log."""
    from adapt.audit.audit_log import record

    frozen = contract.frozen_constraints

    tool_args = action.get("tool_args") or action.get("arguments") or {}
    if not isinstance(tool_args, dict):
        tool_args = {}

    target_host = action.get("target_host") or tool_args.get("target_host")
    if target_host and isinstance(target_host, str) and _host_is_prohibited(target_host, frozen.prohibited_subnets):
        reason = f"target_host '{target_host}' is in a prohibited subnet"
        record(action, reason)
        return EnforcementResult.blocked(reason)

    tool = action.get("tool") or action.get("tool_name", "")
    if tool and isinstance(tool, str):
        for rule in frozen.absolute_rules:
            if tool.lower() in rule.lower():
                reason = f"violates absolute rule: {rule!r}"
                record(action, reason)
                return EnforcementResult.blocked(reason)

    elapsed = action.get("elapsed_time_s", 0)
    if isinstance(elapsed, (int, float)) and elapsed > frozen.max_execution_time_s:
        reason = (
            f"elapsed_time_s={elapsed} exceeds max_execution_time_s="
            f"{frozen.max_execution_time_s}"
        )
        record(action, reason)
        return EnforcementResult.blocked(reason)

    return EnforcementResult.ok()
