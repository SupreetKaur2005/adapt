"""Defines S_cyber, the structured space of techniques CUV scores against."""
from __future__ import annotations

from collections.abc import Iterable

from adapt.schemas import AttackTechnique


class SkillSpace:
    """Holds the filtered technique set from config/mitre_attack_config.yaml."""

    def __init__(self, techniques: list[AttackTechnique]) -> None:
        self._by_id: dict[str, AttackTechnique] = {}
        for technique in techniques:
            # Preserve input order while removing duplicate IDs. An ID is the
            # canonical identity in ATT&CK, so the first record wins.
            self._by_id.setdefault(technique.technique_id, technique)

    @property
    def techniques(self) -> list[AttackTechnique]:
        """Return the current skill space in stable insertion order."""
        return list(self._by_id.values())

    def by_tactic(self, tactic: str) -> list[AttackTechnique]:
        return [t for t in self._by_id.values() if t.tactic == tactic]

    def by_id(self, technique_id: str) -> AttackTechnique | None:
        return self._by_id.get(technique_id)

    @classmethod
    def from_config(cls, techniques: Iterable[AttackTechnique], config_path=None) -> "SkillSpace":
        """Build S_cyber using the configured tactic allowlist.

        Config loading is explicit so callers can also provide a test or
        alternate config without changing process-wide state.
        """
        from pathlib import Path

        import yaml

        path = Path(config_path) if config_path is not None else Path(__file__).resolve().parents[3] / "config" / "mitre_attack_config.yaml"
        with path.open(encoding="utf-8") as stream:
            config = yaml.safe_load(stream) or {}
        allowed_tactics = set(config.get("tactics", []))
        return cls([t for t in techniques if not allowed_tactics or t.tactic in allowed_tactics])
