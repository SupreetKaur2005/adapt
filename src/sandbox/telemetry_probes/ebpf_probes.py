from __future__ import annotations

from typing import Iterator, Any

from adapt.schemas import TelemetryEvent


def get_ebpf_events() -> Iterator[TelemetryEvent]:
    """Yield sample eBPF-derived telemetry events.

    In a real deployment this would read from bcc/bpftrace programs.
    """
    events = [
        TelemetryEvent(event_id="execve", source="ebpf", host="10.0.0.20", raw={"comm": "bash", "argv": ["/bin/bash"]}),
        TelemetryEvent(event_id="write", source="ebpf", host="10.0.0.20", raw={"file": "/etc/passwd", "count": 1}),
    ]
    for ev in events:
        yield ev