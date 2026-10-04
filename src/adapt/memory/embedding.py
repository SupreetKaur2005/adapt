"""Turns an exploit-patch pair (or a subtask description) into a vector, using
a local embedding model (not an API).
"""
from __future__ import annotations


def embed(text: str) -> list[float]:
    raise NotImplementedError
