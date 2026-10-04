"""Callable tool the Red Team LLM invokes via tool-calling; thin wrapper over
the sandbox's port scanner.
"""
from __future__ import annotations

from adapt.agents.red_team.recon import scan


def port_scan(target_host: str) -> dict:
    result = scan(target_host)
    return {
        "target_host": result.target_host,
        "open_ports": result.open_ports,
        "services": result.services,
    }
