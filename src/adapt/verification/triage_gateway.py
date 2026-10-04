"""The decision point.

On PASS, calls `adapt.memory.csim_store.commit`. On BLOCK, calls
`adapt.audit.audit_log.record` and reverts sandbox state via
`adapt.sandbox.container_manager.reset`.
"""
from __future__ import annotations

from adapt.schemas import RoEContract, TriageOutcome


def triage(red_outcome: dict, blue_outcome: dict, contract: RoEContract) -> TriageOutcome:
    raise NotImplementedError
