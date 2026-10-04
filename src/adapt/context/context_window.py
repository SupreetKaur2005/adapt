"""Trims/summarizes older history when it would exceed the current model's
context window -- matters more here than with API models, since local tiers
have materially smaller windows.
"""
from __future__ import annotations

from adapt.context.context_manager import Context

# Rough chars-per-token heuristic for local-model prompt sizing -- no
# tokenizer dependency needed for a pre-flight trim.
_CHARS_PER_TOKEN = 4


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // _CHARS_PER_TOKEN)


def fit_to_window(context: Context, max_tokens: int) -> Context:
    """Drop oldest history turns (keeping the system prompt intact) until the
    estimated token count fits within `max_tokens`.
    """
    budget = max_tokens - _estimate_tokens(context.system_prompt)

    kept: list[dict] = []
    used = 0
    for turn in reversed(context.history):
        turn_tokens = _estimate_tokens(str(turn.get("content", "")))
        if used + turn_tokens > budget:
            break
        kept.append(turn)
        used += turn_tokens
    kept.reverse()

    return Context(
        system_prompt=context.system_prompt,
        history=kept,
        contract_state=context.contract_state,
        tool_schemas=context.tool_schemas,
    )
