"""Queues GPU access across agents so local models don't collide."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from adapt.routing.model_router import ModelHandle


@contextmanager
def acquire(model_handle: ModelHandle) -> Iterator[ModelHandle]:
    """Use as a `with` block around inference calls."""
    raise NotImplementedError
    yield model_handle
