"""Wrapper around transformers/vLLM for any model pulled directly from Hugging
Face rather than through Ollama.

`transformers` is a heavy optional dependency, so it's imported lazily on
first use rather than at module load time.
"""
from __future__ import annotations

from typing import Any


class HFClient:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._pipeline = None

    def _pipe(self):
        if self._pipeline is None:
            from transformers import pipeline

            self._pipeline = pipeline("text-generation", model=self.model_name)
        return self._pipeline

    def generate(self, prompt: str, **kwargs: Any) -> str:
        outputs = self._pipe()(prompt, **kwargs)
        return outputs[0]["generated_text"]
