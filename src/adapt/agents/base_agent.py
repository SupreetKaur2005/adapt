"""Shared ReAct-style loop (Thought -> Action -> Observation), used by both Red
and Blue agent classes so the reasoning pattern isn't duplicated.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Protocol

from adapt.context.context_manager import Context

_THOUGHT_RE = re.compile(r"Thought:\s*(.*)")
_ACTION_RE = re.compile(r"Action:\s*(\S+)")
_ACTION_INPUT_RE = re.compile(r"Action Input:\s*(\{.*\})", re.DOTALL)


@dataclass
class Action:
    thought: str
    tool_name: str
    tool_args: dict


class ModelClient(Protocol):
    def generate(self, model: str, prompt: str, **kwargs: Any) -> str: ...


def render_prompt(context: Context) -> str:
    """Flatten a Context into the single text prompt sent to a local model."""
    lines = [context.system_prompt, ""]
    for turn in context.history:
        role = turn.get("role", "observation")
        content = turn.get("content", "")
        lines.append(f"{role}: {content}")
    lines.append("Thought:")
    return "\n".join(lines)


def parse_response(text: str) -> Action:
    """Parse a model's raw text output into an `Action`.

    Expects the `Thought: / Action: / Action Input:` format spelled out in
    `context.prompt_templates`.
    """
    action_match = _ACTION_RE.search(text)
    if not action_match:
        raise ValueError(f"could not parse an Action from model output: {text!r}")

    thought_match = _THOUGHT_RE.search(text)
    thought = thought_match.group(1).strip() if thought_match else ""

    tool_args: dict = {}
    input_match = _ACTION_INPUT_RE.search(text)
    if input_match:
        try:
            tool_args = json.loads(input_match.group(1))
        except json.JSONDecodeError:
            tool_args = {}

    return Action(thought=thought, tool_name=action_match.group(1).strip(), tool_args=tool_args)


class Agent:
    """Looped by the orchestrator until it emits a terminal action for the round."""

    def __init__(self, model_client: ModelClient, model_name: str) -> None:
        self.model_client = model_client
        self.model_name = model_name

    def step(self, context: Context) -> Action:
        prompt = render_prompt(context)
        response = self.model_client.generate(self.model_name, prompt)
        return parse_response(response)
