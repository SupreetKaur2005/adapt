"""Actively generates new `.pcap` traces at runtime using Impacket, inside the
Mininet sandbox -- not a static-file loader.

This is what actually produces AD-attack network traffic for Red Team to
execute and Blue Team to observe, rather than replaying static files.
"""
from __future__ import annotations

from pathlib import Path


def generate_trace(attack_type: str, target_host: str) -> Path:
    raise NotImplementedError
