"""Probe definitions and C source loader for ADAPT eBPF sensors.

Defines the probe metadata, tracepoints, and filtering rules matching the
sensor configuration shape established in `sysmon_linux_config.py`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProbeDefinition:
    """Metadata describing a single eBPF sensor probe."""

    name: str
    event_type: str
    tracepoint: str
    description: str
    c_source_file: str
    filter_rules: dict[str, Any] = field(default_factory=dict)


_PROBES_DIR = Path(__file__).resolve().parent

DEFAULT_PROBES: dict[str, ProbeDefinition] = {
    "process_exec": ProbeDefinition(
        name="process_exec",
        event_type="ProcessCreate",
        tracepoint="syscalls/sys_enter_execve",
        description="Captures new process executions matching shell and credential tool signatures",
        c_source_file="process_exec.bpf.c",
        filter_rules={
            "images": ["/bin/sh", "/bin/bash", "powershell", "pwsh"],
            "command_line_keywords": ["kerberoast", "mimikatz"],
        },
    ),
    "network_connect": ProbeDefinition(
        name="network_connect",
        event_type="NetworkConnect",
        tracepoint="syscalls/sys_enter_connect",
        description="Captures TCP connections to Kerberos, LDAP, and SMB enterprise services",
        c_source_file="network_connect.bpf.c",
        filter_rules={
            "destination_ports": [88, 389, 445],
            "protocols": ["TCP"],
        },
    ),
    "process_access": ProbeDefinition(
        name="process_access",
        event_type="ProcessAccess",
        tracepoint="syscalls/sys_enter_ptrace",
        description="Captures ptrace attempts targeting credential stores such as lsass",
        c_source_file="process_access.bpf.c",
        filter_rules={
            "target_images": ["lsass"],
            "granted_access": ["0x1400"],
        },
    ),
}


def get_probe_definition(name: str) -> ProbeDefinition | None:
    """Look up a probe definition by its identifier."""
    return DEFAULT_PROBES.get(name)


def list_probe_names() -> list[str]:
    """Return all registered probe names."""
    return list(DEFAULT_PROBES.keys())


def get_probe_c_source(name: str) -> str:
    """Return the raw C source string for a registered probe.

    Raises:
        KeyError: If probe name is not known.
        FileNotFoundError: If the .bpf.c file cannot be found.
    """
    probe = DEFAULT_PROBES.get(name)
    if probe is None:
        raise KeyError(f"Unknown eBPF probe name: {name!r}. Available: {list_probe_names()}")

    source_path = _PROBES_DIR / probe.c_source_file
    if not source_path.is_file():
        raise FileNotFoundError(f"eBPF C source file not found at {source_path}")

    return source_path.read_text(encoding="utf-8")
