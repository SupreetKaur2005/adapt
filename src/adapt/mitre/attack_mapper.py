"""Maps a natural-language subtask description onto MITRE ATT&CK techniques.

e.g. "attempt credential extraction on DC01" -> [T1558, ...]. Likely
implemented as embedding similarity against technique descriptions loaded by
`adapt.datasets.mitre_attack_loader` (actually under the top-level
`datasets/` package).
"""
from __future__ import annotations

from adapt.schemas import AttackTechnique


def map_to_technique(subtask: str) -> list[AttackTechnique]:
    raise NotImplementedError
