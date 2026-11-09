from __future__ import annotations

from typing import Iterator

from adapt.schemas import TelemetryEvent


def live_stream() -> Iterator[TelemetryEvent]:
    """Yield sample telemetry events."""
    events = [
        TelemetryEvent(event_id="4769", source="winrm", host="10.0.0.10", raw={"user": "alice", "service": "ldap"}),
        TelemetryEvent(event_id="1", source="kernel", host="10.0.0.12", raw={"syscall": "execve", "argv": ["/bin/sh"]}),
    ]
    for ev in events:
        yield ev