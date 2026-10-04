"""Tests for `adapt.context.context_manager`."""
from adapt.context.context_manager import build_context
from adapt.orchestrator import EpisodeState
from adapt.schemas import FrozenConstraints, RevisableStrategy, RoEContract


def _episode_state() -> EpisodeState:
    contract = RoEContract(
        frozen_constraints=FrozenConstraints(
            intent="test episode",
            prohibited_subnets=[],
            max_execution_time_s=60,
            absolute_rules=[],
        ),
        revisable_strategy=RevisableStrategy(objective="recon ws01", verification_criteria=[]),
    )
    return EpisodeState(contract=contract, history=[{"role": "observation", "content": "x"}])


def test_build_context_red_team():
    ctx = build_context("red", _episode_state(), tier="lightweight")
    assert "Red Team" in ctx.system_prompt
    assert ctx.contract_state["frozen_constraints"]["intent"] == "test episode"
    assert ctx.tool_schemas
    assert ctx.history == [{"role": "observation", "content": "x"}]


def test_build_context_blue_team_uses_blue_tools():
    ctx = build_context("blue", _episode_state(), tier="mid")
    assert "Blue Team" in ctx.system_prompt
    tool_names = {schema["name"] for schema in ctx.tool_schemas}
    assert "telemetry_query" in tool_names


def test_build_context_falls_back_to_mid_for_unknown_tier():
    ctx = build_context("red", _episode_state(), tier="nonexistent")
    assert ctx.system_prompt  # falls back rather than KeyError
