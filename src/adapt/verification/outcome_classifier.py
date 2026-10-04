"""Conservative classifiers for explicit action and telemetry evidence."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_RED_SUCCESS_KEYS = ("red_success", "exploit_success", "compromised", "credential_captured", "access_granted", "payload_executed", "command_executed")
_BLUE_SUCCESS_KEYS = ("blue_success", "defense_success", "patch_applied", "patch_deployed", "blocked", "prevented", "contained", "remediated", "quarantined", "attack_detected")
_RED_EVENTS = ("exploit_success", "compromise", "credential_captured", "access_granted", "command_executed", "payload_executed")
_BLUE_EVENTS = ("blocked", "prevented", "contained", "remediated", "patch_applied", "patch_deployed", "quarantined", "attack_detected")


def _truth(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "success", "succeeded", "passed", "blocked", "detected", "contained", "remediated"}
    return False


def _walk(value: Any):
    """Yield dictionaries nested under common result/telemetry wrappers."""
    if isinstance(value, Mapping):
        yield value
        for key in ("result", "data", "raw", "details", "evidence"):
            if key in value:
                yield from _walk(value[key])


def _has_success(
    actions: list[dict], telemetry: list[dict], event_markers: tuple[str, ...], *, red_evidence: bool = False
) -> bool:
    for item in [*actions, *telemetry]:
        for record in _walk(item):
            for key in (_RED_SUCCESS_KEYS if red_evidence else _BLUE_SUCCESS_KEYS):
                if key in record and _truth(record[key]):
                    return True
            labels = [
                "_" + "_".join(str(record.get(key, "")).lower().replace("-", "_").split()) + "_"
                for key in ("event", "event_type", "event_name", "action", "outcome")
            ]
            if any(f"_{marker}_" in label for marker in event_markers for label in labels):
                return True
    return False


def classify_red_outcome(actions: list[dict], telemetry: list[dict]) -> bool:
    """True only when action results or telemetry explicitly confirm Red success."""
    if not isinstance(actions, list) or not isinstance(telemetry, list):
        raise TypeError("actions and telemetry must be lists")
    # A generic successful tool call (for example, a completed port scan) is
    # not proof that the target was compromised.
    return _has_success(actions, telemetry, _RED_EVENTS, red_evidence=True)


def classify_blue_outcome(actions: list[dict], telemetry: list[dict]) -> bool:
    """True when Blue reports success or telemetry confirms a defensive outcome."""
    if not isinstance(actions, list) or not isinstance(telemetry, list):
        raise TypeError("actions and telemetry must be lists")
    # A successful defensive result must be explicit; mere tool completion is
    # not evidence that detection, blocking, or remediation worked.
    return _has_success(actions, telemetry, _BLUE_EVENTS)
