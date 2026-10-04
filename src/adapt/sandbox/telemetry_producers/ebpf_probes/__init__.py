"""eBPF sensor probes and probe manager for sandbox telemetry."""
from __future__ import annotations

from adapt.sandbox.telemetry_producers.ebpf_probes.manager import (
    EBPFProbeManager,
    is_ebpf_available,
    is_linux,
    is_root,
)
from adapt.sandbox.telemetry_producers.ebpf_probes.probe_specs import (
    DEFAULT_PROBES,
    ProbeDefinition,
    get_probe_c_source,
    get_probe_definition,
    list_probe_names,
)


def get_ebpf_manager(mock: bool = True, host: str = "10.0.0.5") -> EBPFProbeManager:
    """Create an eBPF probe manager instance with safe mock defaults."""
    return EBPFProbeManager(mock=mock, host=host)


__all__ = [
    "DEFAULT_PROBES",
    "EBPFProbeManager",
    "ProbeDefinition",
    "get_ebpf_manager",
    "get_probe_c_source",
    "get_probe_definition",
    "is_ebpf_available",
    "is_linux",
    "is_root",
    "list_probe_names",
]
