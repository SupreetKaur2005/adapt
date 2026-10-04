"""Shared ReAct-style loop (Thought -> Action -> Observation), used by both Red
and Blue agent classes so the reasoning pattern isn't duplicated.
"""
from __future__ import annotations

from dataclasses import dataclass

from adapt.context.context_manager import Context


@dataclass
class Action:
    thought: str
    tool_name: str
    tool_args: dict


class Agent:
    """Looped by the orchestrator until it emits a terminal action for the round."""

    def step(self, context: Context) -> Action:
        raise NotImplementedError
