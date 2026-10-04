"""Builds the actual prompt context for a given agent call: system prompt +
relevant history + current contract state + relevant tool schemas.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Context:
    system_prompt: str
    history: list[dict]
    contract_state: dict
    tool_schemas: list[dict]


def build_context(agent_role: str, episode_state: Any, tier: str = "mid") -> Context:
    """system prompt + relevant history + current contract state + tool schemas.

    `tier` (lightweight/mid/heavy) picks the prompt variant and would
    normally come from the `ModelHandle` `routing.model_router.route` just
    returned for this round.
    """
    from adapt.context.prompt_templates import BLUE_TEAM_TEMPLATES, RED_TEAM_TEMPLATES

    templates = RED_TEAM_TEMPLATES if agent_role == "red" else BLUE_TEAM_TEMPLATES
    system_prompt = templates.get(tier, templates["mid"])

    contract = getattr(episode_state, "contract", None)
    contract_state = contract.model_dump() if contract is not None else {}

    if agent_role == "red":
        from adapt.agents.red_team.tools.tool_schema import RED_TEAM_TOOL_SCHEMAS as tool_schemas
    else:
        from adapt.agents.blue_team.tools.tool_schema import (
            BLUE_TEAM_TOOL_SCHEMAS as tool_schemas,
        )

    history = list(getattr(episode_state, "history", []))

    return Context(
        system_prompt=system_prompt,
        history=history,
        contract_state=contract_state,
        tool_schemas=tool_schemas,
    )
