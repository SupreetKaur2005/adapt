"""Builds the Mininet network fabric the AD lab and Impacket traces run over."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def build_topology(config_path: Path | str) -> Any:
    """config: config/sandbox_topology.yaml -> Network."""
    raise NotImplementedError
