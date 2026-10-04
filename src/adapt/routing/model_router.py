"""Given a CUV score, picks a tier from config/model_registry.yaml and returns
the actual model handle.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelHandle:
    tier: str
    model_name: str


def route(subtask: str) -> ModelHandle:
    raise NotImplementedError
