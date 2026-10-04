from __future__ import annotations

from adapt.agents.blue_team.telemetry_ingest import ingest_events


def test_ingest_events():
    events = list(ingest_events())
    assert isinstance(events, list)
    assert len(events) == 0


def test_ingest_events_with_source():
    from adapt.agents.blue_team.tools.telemetry_query_tool import clear_telemetry, telemetry_query
    from adapt.schemas import TelemetryEvent

    clear_telemetry()
    raw = [
        TelemetryEvent(event_id="EVT-100", source="ebpf", host="10.0.0.5", raw={"network": "port 88 SYN"}),
        TelemetryEvent(event_id="EVT-101", source="sysmon", host="10.0.0.1", raw={"exec": "execve /bin/sh"}),
    ]
    consumed = list(ingest_events(raw))
    assert len(consumed) == 2
    assert consumed[0].event_id == "EVT-100"

    # Verify buffered into telemetry_query_tool
    found = telemetry_query("execve")
    assert len(found) == 1
    assert found[0]["event_id"] == "EVT-101"
