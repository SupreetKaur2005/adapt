"""Tool the Blue Team LLM invokes to query ingested telemetry."""
from __future__ import annotations


def telemetry_query(filter_expr: str) -> list[dict]:
    raise NotImplementedError
