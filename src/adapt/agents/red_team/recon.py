"""Scans the current sandbox target for open ports, services, and known entry points."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReconResult:
    target_host: str
    open_ports: list[int]
    services: list[str]


def scan(target_host: str) -> ReconResult:
    raise NotImplementedError
