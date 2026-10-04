"""Telemetry producers generating events for Blue Team ingestion (eBPF + Sysmon-Linux)."""
from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from adapt.sandbox.telemetry_producers.ebpf_probes import (
    DEFAULT_PROBES,
    EBPFProbeManager,
    ProbeDefinition,
    get_ebpf_manager,
    get_probe_c_source,
    get_probe_definition,
    is_ebpf_available,
    is_linux,
    is_root,
    list_probe_names,
)
from adapt.schemas import TelemetryEvent

if TYPE_CHECKING:
    pass

_ACTIVE_PRODUCER: EBPFProbeManager | None = None


def set_active_producer(producer: EBPFProbeManager | None) -> None:
    """Set the currently active telemetry producer."""
    global _ACTIVE_PRODUCER
    _ACTIVE_PRODUCER = producer


def get_active_producer() -> EBPFProbeManager | None:
    """Get the currently active telemetry producer, if any."""
    return _ACTIVE_PRODUCER


def live_stream() -> Iterator[TelemetryEvent]:
    """Yield live telemetry events from the active producer.

    If no producer is active or running, yields nothing.
    """
    global _ACTIVE_PRODUCER
    if _ACTIVE_PRODUCER is not None and getattr(_ACTIVE_PRODUCER, "is_running", False):
        yield from _ACTIVE_PRODUCER.poll_events()


__all__ = [
    "DEFAULT_PROBES",
    "EBPFProbeManager",
    "ProbeDefinition",
    "get_active_producer",
    "get_ebpf_manager",
    "get_probe_c_source",
    "get_probe_definition",
    "is_ebpf_available",
    "is_linux",
    "is_root",
    "list_probe_names",
    "live_stream",
    "set_active_producer",
]
