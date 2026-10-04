"""The single enforcement point (v2 had this duplicated across two files --
fixed here).
"""
from __future__ import annotations

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


def check(action: dict, contract: RoEContract) -> EnforcementResult:
    """Check an action against the contract. On BLOCKED, writes to adapt.audit.audit_log."""
    raise NotImplementedError
