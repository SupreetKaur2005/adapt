"""Wrapper around transformers/vLLM for any model pulled directly from Hugging
Face rather than through Ollama.
"""
from __future__ import annotations

from typing import Any


class HFClient:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def generate(self, prompt: str, **kwargs: Any) -> str:
        raise NotImplementedError
