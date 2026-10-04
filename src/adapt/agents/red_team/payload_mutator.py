"""Mutates a candidate exploit across attempts, seeded by Atomic Red Team
playbooks so mutations stay realistic rather than arbitrary. Triggered
specifically on a PIVOT outcome.

Falls back to a clearly-labeled deterministic mutation until
`datasets.atomic_redteam_loader` is implemented -- no coordination needed
with whoever builds that, this upgrades automatically once it lands.
"""
from __future__ import annotations

from typing import Any

from adapt.schemas import ExploitAttempt


class _ModelClient:
    def generate(self, model: str, prompt: str, **kwargs: Any) -> str: ...


def _naive_mutate(payload: str) -> str:
    return f"{payload}  # mutated-variant (no Atomic Red Team seed available yet)"


def mutate(
    exploit: ExploitAttempt,
    technique_id: str,
    model_client: _ModelClient | None = None,
) -> ExploitAttempt:
    from datasets.atomic_redteam_loader import load_playbooks

    try:
        playbooks = load_playbooks(technique_id)
    except NotImplementedError:
        playbooks = []

    if not playbooks:
        return ExploitAttempt(
            subtask=exploit.subtask,
            technique=exploit.technique,
            payload=_naive_mutate(exploit.payload),
            model_used=exploit.model_used,
        )

    from adapt.routing.model_router import route
    from adapt.routing.model_scheduler import acquire

    if model_client is None:
        from adapt.routing.model_clients.ollama_client import OllamaClient

        model_client = OllamaClient()

    handle = route(exploit.subtask, technique=exploit.technique)
    seed = playbooks[0]
    prompt = (
        "Previous exploit attempt failed and must be mutated (PIVOT):\n"
        f"{exploit.payload}\n\n"
        f"Seed variant from Atomic Red Team ({technique_id}): {seed.command}\n"
        "Propose a mutated payload inspired by the seed variant. Respond with only the payload."
    )

    with acquire(handle):
        mutated_payload = model_client.generate(handle.model_name, prompt).strip()

    return ExploitAttempt(
        subtask=exploit.subtask,
        technique=exploit.technique,
        payload=mutated_payload,
        model_used=handle.model_name,
    )
