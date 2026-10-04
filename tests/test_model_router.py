"""Tests for `adapt.routing.model_router`."""
from adapt.routing.model_router import ModelHandle, route, tier_for_model
from adapt.schemas import AttackTechnique


def test_tier_for_model_known_model():
    assert tier_for_model("qwen2.5:0.5b") == "lightweight"


def test_route_returns_handle_from_registry():
    technique = AttackTechnique(technique_id="T1046", name="recon", tactic="discovery")
    handle = route("scan ws01 for open ports", technique=technique)
    assert isinstance(handle, ModelHandle)
    assert handle.tier in {"lightweight", "mid", "heavy"}
