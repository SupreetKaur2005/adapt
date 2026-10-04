"""Queues GPU access across agents so local models don't collide.

Process-local only: one `threading.Lock` per tier. Good enough for a single
orchestrator process running Red/Blue/embedding calls concurrently; a
multi-process deployment would need a cross-process lock (e.g. a file lock
or a lightweight lock service) instead.
"""
from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Iterator

from adapt.routing.model_router import ModelHandle

_locks_guard = threading.Lock()
_tier_locks: dict[str, threading.Lock] = {}


def _lock_for_tier(tier: str) -> threading.Lock:
    with _locks_guard:
        if tier not in _tier_locks:
            _tier_locks[tier] = threading.Lock()
        return _tier_locks[tier]


@contextmanager
def acquire(model_handle: ModelHandle) -> Iterator[ModelHandle]:
    """Use as a `with` block around inference calls."""
    lock = _lock_for_tier(model_handle.tier)
    lock.acquire()
    try:
        yield model_handle
    finally:
        lock.release()
