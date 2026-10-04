"""Defines S_cyber, the structured space of techniques CUV scores against."""
from __future__ import annotations

from adapt.schemas import AttackTechnique


class SkillSpace:
    """Holds the filtered technique set from config/mitre_attack_config.yaml."""

    def __init__(self, techniques: list[AttackTechnique]) -> None:
        self._by_id = {t.technique_id: t for t in techniques}

    def by_tactic(self, tactic: str) -> list[AttackTechnique]:
        return [t for t in self._by_id.values() if t.tactic == tactic]

    def by_id(self, technique_id: str) -> AttackTechnique | None:
        return self._by_id.get(technique_id)
