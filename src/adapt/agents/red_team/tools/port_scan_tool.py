"""Callable tool the Red Team LLM invokes via tool-calling; thin wrapper over
the sandbox's port scanner.
"""
from __future__ import annotations


def port_scan(target_host: str) -> dict:
    raise NotImplementedError
