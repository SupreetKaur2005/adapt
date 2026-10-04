"""Loads the MITRE ATT&CK STIX bundle via the `stix2` library.

Output feeds `adapt.mitre.skill_space`.
"""
from __future__ import annotations

from pathlib import Path

from adapt.schemas import AttackTechnique


def load_attack_techniques(bundle_path: Path | str) -> list[AttackTechnique]:
    """Parse the local STIX bundle at `bundle_path` into `AttackTechnique` models."""
    raise NotImplementedError
