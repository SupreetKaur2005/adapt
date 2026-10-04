"""Thin wrapper around local vector store, running fully local -- no external
service dependency.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))


class VectorDBClient:
    def __init__(self, persist_dir: str | Path) -> None:
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.persist_dir / "vectors.json"
        self._items: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self._items = json.load(f)
            except Exception:
                self._items = {}

    def _save(self) -> None:
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self._items, f, indent=2)
        except Exception:
            pass

    def upsert(self, doc_id: str, embedding: list[float], metadata: dict[str, Any]) -> None:
        self._items[doc_id] = {
            "id": doc_id,
            "embedding": embedding,
            "metadata": metadata,
        }
        self._save()

    def query(self, embedding: list[float], top_k: int = 5) -> list[dict]:
        scored: list[tuple[float, dict]] = []
        for item in self._items.values():
            sim = _cosine(embedding, item.get("embedding", []))
            scored.append((sim, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:top_k]]
