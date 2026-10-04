"""Enforces the sealed-box network boundary -- the actual firewall/namespace
rules preventing sandbox traffic from reaching the host.
"""
from __future__ import annotations


def seal_network(namespace: str) -> None:
    raise NotImplementedError
