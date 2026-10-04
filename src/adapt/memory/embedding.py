"""Turns an exploit-patch pair (or a subtask description) into a vector, using
a local embedding model.
"""
from __future__ import annotations

import hashlib
import math
import re

DIMENSION = 64


def embed(text: str) -> list[float]:
    """Generate a deterministic local vector embedding for text."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    tokens = re.findall(r"\w+", text.lower())
    if not tokens:
        return [0.0] * DIMENSION

    vec = [0.0] * DIMENSION
    for token in tokens:
        h = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
        idx = h % DIMENSION
        sign = 1.0 if (h >> 8) & 1 else -1.0
        vec[idx] += sign

    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec
