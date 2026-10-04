"""Builds the actual prompt context for a given agent call: system prompt +
relevant history + current contract state + relevant tool schemas.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Context:
    system_prompt: str
    history: list[dict]
    contract_state: dict
    tool_schemas: list[dict]


def build_context(agent_role: str, episode_state) -> Context:
    raise NotImplementedError
