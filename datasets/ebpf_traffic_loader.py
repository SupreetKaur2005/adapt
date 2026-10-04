"""Loads the labeled eBPF/XDP traffic dataset.

Used as ground truth in container-isolation tests to confirm the sandbox's
network isolation is actually working (i.e. no traffic escapes that
shouldn't).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_ebpf_traffic(path: Path | str) -> pd.DataFrame:
    raise NotImplementedError
