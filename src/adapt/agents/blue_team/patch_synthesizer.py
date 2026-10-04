"""Given a detected breach + its graph representation, generates a code-level patch."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Patch:
    file_path: str
    diff: str
    description: str


def synthesize_patch(breach: dict, graphs: dict[str, Any]) -> Patch:
    raise NotImplementedError
