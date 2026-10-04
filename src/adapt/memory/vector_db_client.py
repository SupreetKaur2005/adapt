"""Thin wrapper around Chroma, running fully local -- no external service
dependency.
"""
from __future__ import annotations

from typing import Any


class VectorDBClient:
    def __init__(self, persist_dir: str) -> None:
        self.persist_dir = persist_dir

    def upsert(self, doc_id: str, embedding: list[float], metadata: dict[str, Any]) -> None:
        raise NotImplementedError

    def query(self, embedding: list[float], top_k: int = 5) -> list[dict]:
        raise NotImplementedError
