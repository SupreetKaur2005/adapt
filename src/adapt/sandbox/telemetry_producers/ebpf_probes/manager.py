"""EBPFProbeManager for running and mocking Linux eBPF telemetry sensors.

Provides Linux-aware probe lifecycle management, lazy loading of eBPF
libraries (BCC / libbpf), deterministic mock event generation for cross-platform
testing, and schema-compliant TelemetryEvent streaming for Blue Team ingestion.
"""
from __future__ import annotations

import os
import sys
import uuid
from collections import deque
from collections.abc import Iterator
from typing import Any

from adapt.sandbox.telemetry_producers.ebpf_probes.probe_specs import (
    DEFAULT_PROBES,
    ProbeDefinition,
    get_probe_c_source,
    get_probe_definition,
    list_probe_names,
)
from adapt.schemas import TelemetryEvent


def is_linux() -> bool:
    """Return True if running on a Linux platform."""
    return sys.platform.startswith("linux")


def is_root() -> bool:
    """Return True if running with effective root privileges on a POSIX host."""
    if not hasattr(os, "geteuid"):
        return False
    try:
        return os.geteuid() == 0
    except Exception:
        return False


def is_ebpf_available() -> bool:
    """Check if the host environment supports live eBPF probing.

    Requires Linux, root privileges, and the BCC library to be loadable.
    """
    if not is_linux() or not is_root():
        return False
    try:
        # Lazy import of BCC to avoid module load failure on non-Linux systems
        import bcc  # type: ignore # noqa: F401

        return True
    except (ImportError, Exception):
        return False


class EBPFProbeManager:
    """Manages the lifecycle and telemetry output of eBPF sandbox sensors."""

    def __init__(
        self,
        mock: bool = False,
        host: str = "10.0.0.5",
        fallback_to_mock: bool = True,
        enabled_probes: list[str] | None = None,
    ) -> None:
        self.host = host
        self.fallback_to_mock = fallback_to_mock
        self._ebpf_available = is_ebpf_available()

        if mock:
            self.is_mock = True
        elif not self._ebpf_available:
            if self.fallback_to_mock:
                self.is_mock = True
            else:
                raise RuntimeError(
                    "eBPF is not available on this host: requires Linux, root privileges, "
                    "and the BCC/libbpf toolchain."
                )
        else:
            self.is_mock = False

        self._active_probes: set[str] = set()
        requested = enabled_probes if enabled_probes is not None else list_probe_names()
        for probe_name in requested:
            if probe_name in DEFAULT_PROBES:
                self._active_probes.add(probe_name)

        self._is_running: bool = False
        self._event_buffer: deque[TelemetryEvent] = deque()
        self._live_bpf_instances: dict[str, Any] = {}
        self._event_seq: int = 0

    @property
    def is_running(self) -> bool:
        """Whether the probe manager is currently active."""
        return self._is_running

    @property
    def active_probes(self) -> set[str]:
        """Set of probe names currently enabled."""
        return set(self._active_probes)

    def attach_probe(self, name: str) -> bool:
        """Enable an eBPF probe by name."""
        if name not in DEFAULT_PROBES:
            return False
        self._active_probes.add(name)
        if self._is_running and not self.is_mock:
            self._attach_live_probe(name)
        return True

    def detach_probe(self, name: str) -> bool:
        """Disable an eBPF probe by name."""
        if name not in self._active_probes:
            return False
        self._active_probes.remove(name)
        if not self.is_mock and name in self._live_bpf_instances:
            self._detach_live_probe(name)
        return True

    def start(self) -> None:
        """Start the probe manager and begin collecting telemetry."""
        if self._is_running:
            return
        self._is_running = True

        if not self.is_mock:
            for probe_name in list(self._active_probes):
                self._attach_live_probe(probe_name)

    def stop(self) -> None:
        """Stop the probe manager and detach all active probes."""
        if not self._is_running:
            return
        if not self.is_mock:
            for probe_name in list(self._live_bpf_instances.keys()):
                self._detach_live_probe(probe_name)
        self._is_running = False

    def emit_event(self, event: TelemetryEvent) -> None:
        """Manually append a TelemetryEvent to the manager's buffer."""
        self._event_buffer.append(event)

    def poll_events(self, max_events: int = 50) -> list[TelemetryEvent]:
        """Drain up to `max_events` from the collected event buffer."""
        events: list[TelemetryEvent] = []
        while self._event_buffer and len(events) < max_events:
            events.append(self._event_buffer.popleft())
        return events

    def stream_events(self) -> Iterator[TelemetryEvent]:
        """Yield all currently available telemetry events."""
        while self._event_buffer:
            yield self._event_buffer.popleft()

    def generate_mock_event(
        self,
        event_type: str = "ProcessCreate",
        custom_fields: dict[str, Any] | None = None,
    ) -> TelemetryEvent:
        """Generate a single deterministic mock TelemetryEvent matching sensor shapes.

        The produced event format directly aligns with the rules in `sysmon_linux_config.py`.
        """
        self._event_seq += 1
        event_id = f"EBPF-{self._event_seq:04d}"
        raw: dict[str, Any] = {}

        if event_type == "ProcessCreate":
            raw = {
                "event_type": "ProcessCreate",
                "syscall": "execve",
                "image": "/bin/sh",
                "command_line": "/bin/sh -c whoami",
                "pid": 1000 + self._event_seq,
                "ppid": 999,
                "uid": 0,
            }
        elif event_type == "NetworkConnect":
            raw = {
                "event_type": "NetworkConnect",
                "syscall": "connect",
                "destination_ip": "10.0.0.1",
                "destination_port": 88,
                "source_ip": self.host,
                "source_port": 49152 + self._event_seq,
                "protocol": "TCP",
                "pid": 1000 + self._event_seq,
            }
        elif event_type == "ProcessAccess":
            raw = {
                "event_type": "ProcessAccess",
                "syscall": "ptrace",
                "target_image": "lsass",
                "target_pid": 580,
                "granted_access": "0x1400",
                "pid": 1000 + self._event_seq,
            }
        else:
            raw = {
                "event_type": event_type,
                "pid": 1000 + self._event_seq,
            }

        if custom_fields:
            raw.update(custom_fields)

        event = TelemetryEvent(
            event_id=event_id,
            source="ebpf",
            host=self.host,
            raw=raw,
        )
        self.emit_event(event)
        return event

    def generate_mock_batch(self) -> list[TelemetryEvent]:
        """Generate one mock event for each currently active probe."""
        batch: list[TelemetryEvent] = []
        for probe_name in sorted(self._active_probes):
            probe_def = get_probe_definition(probe_name)
            if probe_def:
                batch.append(self.generate_mock_event(event_type=probe_def.event_type))
        return batch

    def _attach_live_probe(self, name: str) -> None:
        """Attach a live eBPF probe using BCC (Linux only)."""
        if self.is_mock:
            return
        try:
            from bcc import BPF  # type: ignore

            c_src = get_probe_c_source(name)
            bpf = BPF(text=c_src)
            self._live_bpf_instances[name] = bpf
        except Exception as exc:
            # Fall back safely without crashing
            self._live_bpf_instances.pop(name, None)
            if not self.fallback_to_mock:
                raise RuntimeError(f"Failed to attach eBPF probe {name!r}: {exc}") from exc

    def _detach_live_probe(self, name: str) -> None:
        """Detach a live eBPF probe."""
        bpf = self._live_bpf_instances.pop(name, None)
        if bpf is not None:
            try:
                bpf.cleanup()
            except Exception:
                pass

    def __enter__(self) -> EBPFProbeManager:
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()
