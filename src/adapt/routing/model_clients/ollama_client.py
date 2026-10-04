"""Thin wrapper around the Ollama HTTP API (generate, chat, tool-calling passthrough)."""
from __future__ import annotations

from typing import Any


class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434") -> None:
        self.host = host

    def generate(self, model: str, prompt: str, **kwargs: Any) -> str:
        raise NotImplementedError

    def chat(self, model: str, messages: list[dict], **kwargs: Any) -> dict:
        raise NotImplementedError
