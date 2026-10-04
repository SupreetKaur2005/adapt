"""Trims/summarizes older history when it would exceed the current model's
context window -- matters more here than with API models, since local tiers
have materially smaller windows.
"""
from __future__ import annotations

from adapt.context.context_manager import Context


def fit_to_window(context: Context, max_tokens: int) -> Context:
    raise NotImplementedError
