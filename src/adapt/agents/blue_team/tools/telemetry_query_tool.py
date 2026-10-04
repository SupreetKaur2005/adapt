"""Tool the Blue Team LLM invokes to query ingested telemetry."""
from __future__ import annotations


_EVENT_STORE: list[dict] = []


def record_telemetry(event: dict) -> None:
    """Buffer a telemetry event into the queryable store."""
    _EVENT_STORE.append(event)


def clear_telemetry() -> None:
    """Clear the buffered telemetry store."""
    _EVENT_STORE.clear()


def telemetry_query(filter_expr: str) -> list[dict]:
    """Query ingested telemetry events by filter expression or keyword."""
    if not filter_expr or filter_expr == "*":
        return list(_EVENT_STORE)

    query = filter_expr.lower().strip()
    matching: list[dict] = []
    for ev in _EVENT_STORE:
        matched = False
        for k, v in ev.items():
            if query in str(k).lower() or query in str(v).lower():
                matched = True
                break
        if matched:
            matching.append(ev)
    return matching

