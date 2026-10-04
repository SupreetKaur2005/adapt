from __future__ import annotations

from adapt.agents.blue_team.tools.telemetry_query_tool import telemetry_query


def test_telemetry_query():
    from adapt.agents.blue_team.tools.telemetry_query_tool import clear_telemetry
    clear_telemetry()
    results = telemetry_query("event_id == '123'")
    assert isinstance(results, list)
    assert len(results) == 0


def test_telemetry_query_with_data():
    from adapt.agents.blue_team.tools.telemetry_query_tool import clear_telemetry, record_telemetry
    clear_telemetry()
    record_telemetry({"event_id": 4769, "service": "krbtgt", "host": "DC01"})
    record_telemetry({"event_id": 4104, "script": "Invoke-Mimikatz", "host": "WS01"})

    all_events = telemetry_query("*")
    assert len(all_events) == 2

    krbtgt_events = telemetry_query("krbtgt")
    assert len(krbtgt_events) == 1
    assert krbtgt_events[0]["event_id"] == 4769

    mimi_events = telemetry_query("mimikatz")
    assert len(mimi_events) == 1
    assert mimi_events[0]["host"] == "WS01"
