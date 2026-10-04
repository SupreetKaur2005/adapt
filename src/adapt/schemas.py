"""Typed Pydantic models shared across every A.D.A.P.T. module.

Every other module imports from here rather than passing loosely-shaped
dicts around -- this is what makes "what does K_t look like in code" a
concrete, answerable question.
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel


class FrozenConstraints(BaseModel):
    """I, C_t: intent + hard constraints. Set once at episode start, never mutated."""

    intent: str
    prohibited_subnets: list[str] = []
    max_execution_time_s: int
    absolute_rules: list[str] = []


class RevisableStrategy(BaseModel):
    """O_t, V_t: current objective + verification criteria. Updatable each round."""

    objective: str
    verification_criteria: list[str] = []


class RoEContract(BaseModel):
    """K_t = (I, O_t, C_t, V_t), split into frozen and revisable tiers."""

    frozen_constraints: FrozenConstraints
    revisable_strategy: RevisableStrategy

    def validate_action(self, action: dict[str, Any]) -> bool:
        """The actual check every agent action passes through.

        Delegates to `adapt.contract.constraint_enforcer.check` -- imported
        lazily here to avoid a schemas <-> contract import cycle.
        """
        from adapt.contract.constraint_enforcer import check

        return check(action, self).allowed


class AttackTechnique(BaseModel):
    technique_id: str
    name: str
    tactic: str
    description: str = ""


class ExploitAttempt(BaseModel):
    subtask: str
    technique: AttackTechnique
    payload: str
    model_used: str


class Verdict(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    PIVOT = "PIVOT"


class TriageOutcome(BaseModel):
    verdict: Verdict
    reason: str = ""
    round_number: int


class CUVScore(BaseModel):
    """CUV = (success_rate x stealth_multiplier) / (cost_per_token x execution_time)."""

    technique_id: str
    success_rate: float
    stealth_multiplier: float
    cost_per_token: float
    execution_time_s: float

    @property
    def value(self) -> float:
        return (self.success_rate * self.stealth_multiplier) / (
            self.cost_per_token * self.execution_time_s
        )


class TelemetryEvent(BaseModel):
    event_id: str
    source: str
    host: str
    raw: dict[str, Any] = {}
