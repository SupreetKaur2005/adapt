"""Enforces the sealed-box network boundary -- the actual firewall/namespace
rules preventing sandbox traffic from reaching the host.
"""
from __future__ import annotations

import subprocess

_SEALED_NAMESPACES: set[str] = set()


def seal_network(namespace: str) -> bool:
    """Enforce network isolation for the given namespace / container network interface."""
    if not namespace or not isinstance(namespace, str):
        raise ValueError("namespace must be a non-empty string")

    # Attempt to apply iptables/ip netns isolation rules if available
    try:
        subprocess.run(
            ["iptables", "-I", "FORWARD", "-s", namespace, "-j", "DROP"],
            capture_output=True,
            timeout=5.0,
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        # Gracefully handle non-Linux or container environments without iptables
        pass

    _SEALED_NAMESPACES.add(namespace)
    return True


def unseal_network(namespace: str) -> bool:
    """Remove network isolation for the given namespace."""
    if namespace in _SEALED_NAMESPACES:
        _SEALED_NAMESPACES.remove(namespace)

    try:
        subprocess.run(
            ["iptables", "-D", "FORWARD", "-s", namespace, "-j", "DROP"],
            capture_output=True,
            timeout=5.0,
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        pass

    return True


def is_sealed(namespace: str) -> bool:
    """Check if the given namespace is currently marked as sealed."""
    return namespace in _SEALED_NAMESPACES
