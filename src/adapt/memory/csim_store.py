"""The "vaccine registry": committed exploit/patch pairs from PASS verdicts."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import uuid

from adapt.schemas import AttackTechnique, ExploitAttempt


@dataclass
class HistoricalRecord:
    exploit: ExploitAttempt
    patch: dict
    outcome: str


_STORE: list[HistoricalRecord] = []
_CLIENT = None


def _get_client():
    global _CLIENT
    if _CLIENT is None:
        from adapt.memory.vector_db_client import VectorDBClient

        persist_dir = Path(__file__).resolve().parents[3] / "data" / "csim_registry"
        _CLIENT = VectorDBClient(persist_dir)
    return _CLIENT


def commit(exploit: ExploitAttempt, patch: dict) -> None:
    """Only ever called from a PASS verdict."""
    record = HistoricalRecord(exploit=exploit, patch=patch, outcome="PASS")
    _STORE.append(record)

    from adapt.memory.embedding import embed

    text = f"{exploit.subtask} {exploit.technique.name} {exploit.payload}"
    vector = embed(text)

    client = _get_client()
    doc_id = str(uuid.uuid4())
    metadata = {
        "subtask": exploit.subtask,
        "technique_id": exploit.technique.technique_id,
        "technique_name": exploit.technique.name,
        "technique_tactic": exploit.technique.tactic,
        "payload": exploit.payload,
        "model_used": exploit.model_used,
        "patch": patch,
        "outcome": "PASS",
    }
    client.upsert(doc_id, vector, metadata)


SIMILARITY_THRESHOLD = 0.2


def clear() -> None:
    """Clear memory store and persistent store (primarily for tests)."""
    global _STORE
    _STORE = []
    client = _get_client()
    client._items = {}
    client._save()


def query_similar(subtask: str, top_k: int = 5) -> list[HistoricalRecord]:
    """Used by `adapt.routing.task_estimator`."""
    if not subtask or not subtask.strip():
        return []

    if _STORE:
        from adapt.memory.embedding import embed
        from adapt.memory.vector_db_client import _cosine

        query_vec = embed(subtask)
        scored = []
        for r in _STORE:
            text = f"{r.exploit.subtask} {r.exploit.technique.name} {r.exploit.payload}"
            r_vec = embed(text)
            sim = _cosine(query_vec, r_vec)
            if sim >= SIMILARITY_THRESHOLD:
                scored.append((sim, r))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:top_k]]

    from adapt.memory.embedding import embed

    client = _get_client()
    query_vec = embed(subtask)
    results = client.query(query_vec, top_k=top_k)

    records: list[HistoricalRecord] = []
    for res in results:
        meta = res.get("metadata", {})
        # Only include if similarity above threshold
        from adapt.memory.vector_db_client import _cosine
        sim = _cosine(query_vec, res.get("embedding", []))
        if sim < SIMILARITY_THRESHOLD:
            continue

        tech = AttackTechnique(
            technique_id=meta.get("technique_id", "T1000"),
            name=meta.get("technique_name", "Unknown"),
            tactic=meta.get("technique_tactic", "unknown"),
        )
        exploit = ExploitAttempt(
            subtask=meta.get("subtask", ""),
            technique=tech,
            payload=meta.get("payload", ""),
            model_used=meta.get("model_used", ""),
        )
        records.append(
            HistoricalRecord(
                exploit=exploit,
                patch=meta.get("patch", {}),
                outcome=meta.get("outcome", "PASS"),
            )
        )
    return records
