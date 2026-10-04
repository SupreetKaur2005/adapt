"""Callable tool the Red Team LLM invokes to execute a payload against a
sandbox target.
"""
from __future__ import annotations


def payload_execute(target_host: str, payload: str) -> dict:
    raise NotImplementedError
