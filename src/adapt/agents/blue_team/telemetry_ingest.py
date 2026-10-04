"""Reads the live event stream from `sandbox.telemetry_producers` (eBPF + Sysmon-Linux)."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Iterator

from adapt.agents.blue_team.tools.telemetry_query_tool import record_telemetry
from adapt.schemas import TelemetryEvent


def ingest_events(source: Iterable[TelemetryEvent] | None = None) -> Iterator[TelemetryEvent]:
    """Ingest telemetry events from an explicit source or live telemetry producers.
    
    Buffers each ingested event into the queryable telemetry store.
    """
    if source is not None:
        for event in source:
            record_telemetry(event.model_dump() if hasattr(event, "model_dump") else dict(event))
            yield event
        return

    # Check for live telemetry producers once Khushi's module lands
    try:
        from adapt.sandbox.telemetry_producers import live_stream

        for event in live_stream():
            record_telemetry(event.model_dump() if hasattr(event, "model_dump") else dict(event))
            yield event
        return
    except (ImportError, AttributeError):
        pass

    yield from []

