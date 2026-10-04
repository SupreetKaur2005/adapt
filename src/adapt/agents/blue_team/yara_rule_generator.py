"""Generates a YARA detection rule from the same breach event, for future
prevention (distinct output from the patch itself).
"""
from __future__ import annotations

from typing import Any


class _ModelClient:
    def generate(self, model: str, prompt: str, **kwargs: Any) -> str: ...


def generate_yara_rule(
    breach: dict, model_client: _ModelClient | None = None
) -> str:
    from adapt.routing.model_router import route
    from adapt.routing.model_scheduler import acquire

    subtask = "generate yara rule for breach"
    handle = route(subtask)

    if model_client is None:
        from adapt.routing.model_clients.ollama_client import OllamaClient

        model_client = OllamaClient()

    prompt = (
        f"Breach details: {breach}\n"
        "Generate a YARA detection rule for this breach event. "
        "Respond with only the raw YARA rule string, no explanation."
    )

    with acquire(handle):
        yara_rule = model_client.generate(handle.model_name, prompt).strip()

    return yara_rule

