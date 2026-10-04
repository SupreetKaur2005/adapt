"""RoEContract: K_t split into FrozenConstraints (I, C_t) and RevisableStrategy
(O_t, V_t). The data shape lives in `adapt.schemas`; re-exported here as this
module's canonical home per the project spec.
"""
from __future__ import annotations

from adapt.schemas import FrozenConstraints, RevisableStrategy, RoEContract

__all__ = ["RoEContract", "FrozenConstraints", "RevisableStrategy"]
