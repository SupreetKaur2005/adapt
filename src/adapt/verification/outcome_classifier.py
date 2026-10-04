"""Determines, from raw agent actions and telemetry, whether Red actually
succeeded and whether Blue actually succeeded -- the inputs `triage_gateway.py`
needs. This is where "did the exploit really work" gets decided, separate
from the triage logic itself.
"""
from __future__ import annotations


def classify_red_outcome(actions: list[dict], telemetry: list[dict]) -> bool:
    raise NotImplementedError


def classify_blue_outcome(actions: list[dict], telemetry: list[dict]) -> bool:
    raise NotImplementedError
