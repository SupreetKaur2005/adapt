from __future__ import annotations

from typing import Iterator, Any

from adapt.schemas import TelemetryEvent


def get_sysmon_events() -> Iterator[TelemetryEvent]:
    """Yield sample Sysmon-Linux telemetry events.

    In a real deployment this would read from the Sysmon-Linux forwarder.
    """
    events = [
        TelemetryEvent(event_id="file_create", source="sysmon", host="10.0.0.21", raw={"target_file": "/tmp/test.exe"}),
        TelemetryEvent(event_id="process_start", source="sysmon", host="10.0.0.21", raw={"parent_process": "init", "process": "ssh"}),
    ]
    for ev in events:
        yield ev