"""Given a CUV score, picks a tier from config/model_registry.yaml and returns
the actual model handle.
"""
from __future__ import annotations

import functools
from dataclasses import dataclass
from pathlib import Path

import yaml

from adapt.schemas import AttackTechnique

_REGISTRY_PATH = Path(__file__).resolve().parents[3] / "config" / "model_registry.yaml"


@dataclass
class ModelHandle:
    tier: str
    model_name: str


@functools.lru_cache(maxsize=1)
def load_registry() -> dict:
    """Read config/model_registry.yaml. Cached -- call `load_registry.cache_clear()`
    in tests that need to reload it.
    """
    with _REGISTRY_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def tier_for_model(model_name: str) -> str:
    registry = load_registry()
    for tier_name, tier_cfg in registry["tiers"].items():
        if model_name in tier_cfg["models"]:
            return tier_name
    raise ValueError(f"model {model_name!r} not found in any tier")


def route(subtask: str, technique: AttackTechnique | None = None) -> ModelHandle:
    """Score every model across every tier via CUV and return the best handle.

    If `technique` isn't supplied, attempt to map the subtask onto an ATT&CK
    technique; falls back to a placeholder technique if the mapper isn't
    built yet, so routing works standalone today and improves automatically
    once `mitre.attack_mapper` is implemented.
    """
    from adapt.routing.cuv_calculator import compute_cuv

    if technique is None:
        try:
            from adapt.mitre.attack_mapper import map_to_technique

            techniques = map_to_technique(subtask)
            technique = techniques[0] if techniques else None
        except NotImplementedError:
            technique = None
        if technique is None:
            technique = AttackTechnique(
                technique_id="UNKNOWN", name="unknown", tactic="discovery"
            )

    registry = load_registry()
    best_tier: str | None = None
    best_model: str | None = None
    best_score = float("-inf")

    for tier_name, tier_cfg in registry["tiers"].items():
        for model_name in tier_cfg["models"]:
            score = compute_cuv(subtask, technique, model_name)
            if score > best_score:
                best_score = score
                best_tier = tier_name
                best_model = model_name

    if best_tier is None or best_model is None:
        raise ValueError("no models found in model_registry.yaml")

    return ModelHandle(tier=best_tier, model_name=best_model)
