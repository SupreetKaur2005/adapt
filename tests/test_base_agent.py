"""Tests for `adapt.agents.base_agent`."""
import pytest

from adapt.agents.base_agent import Agent, parse_response, render_prompt
from adapt.context.context_manager import Context


def test_parse_response_extracts_action():
    text = 'Thought: scan first\nAction: port_scan\nAction Input: {"target_host": "ws01"}'
    action = parse_response(text)
    assert action.thought == "scan first"
    assert action.tool_name == "port_scan"
    assert action.tool_args == {"target_host": "ws01"}


def test_parse_response_without_action_raises():
    with pytest.raises(ValueError):
        parse_response("just some text with no Action line")


def test_parse_response_tolerates_malformed_json_input():
    action = parse_response("Thought: hm\nAction: recon\nAction Input: {not json}")
    assert action.tool_name == "recon"
    assert action.tool_args == {}


def test_render_prompt_includes_system_prompt_and_history():
    context = Context(
        system_prompt="SYS PROMPT",
        history=[{"role": "observation", "content": "nothing found"}],
        contract_state={},
        tool_schemas=[],
    )
    prompt = render_prompt(context)
    assert prompt.startswith("SYS PROMPT")
    assert "observation: nothing found" in prompt
    assert prompt.rstrip().endswith("Thought:")


class _FakeModelClient:
    def generate(self, model, prompt, **kwargs):
        return "Thought: ok\nAction: recon\nAction Input: {}"


def test_agent_step_returns_parsed_action():
    agent = Agent(model_client=_FakeModelClient(), model_name="mistral:7b")
    context = Context(system_prompt="SYS", history=[], contract_state={}, tool_schemas=[])
    action = agent.step(context)
    assert action.tool_name == "recon"
