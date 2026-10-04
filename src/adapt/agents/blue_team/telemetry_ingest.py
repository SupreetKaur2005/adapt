"""Reads the live event stream from `sandbox.telemetry_producers` (eBPF + Sysmon-Linux)."""
from __future__ import annotations

from typing import Iterator

from adapt.schemas import TelemetryEvent


def ingest_events() -> Iterator[TelemetryEvent]:
    raise NotImplementedError
