"""Thin wrapper around the Ollama HTTP API (generate, chat, tool-calling passthrough).

Uses the `ollama` package (declared in pyproject.toml) rather than raw HTTP,
imported lazily so this module is importable even where `ollama` isn't
installed (e.g. unit tests that mock `OllamaClient` entirely).
"""
from __future__ import annotations

from typing import Any


class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434") -> None:
        import ollama

        self._client = ollama.Client(host=host)

    def generate(self, model: str, prompt: str, **kwargs: Any) -> str:
        response = self._client.generate(model=model, prompt=prompt, **kwargs)
        return response["response"]

    def chat(self, model: str, messages: list[dict], **kwargs: Any) -> dict:
        return self._client.chat(model=model, messages=messages, **kwargs)
