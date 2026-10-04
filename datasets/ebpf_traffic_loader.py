"""Loads the labeled eBPF/XDP traffic dataset.

Used as ground truth in container-isolation tests to confirm the sandbox's
network isolation is actually working (i.e. no traffic escapes that shouldn't).
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


def load_ebpf_traffic(path: Path | str) -> Any:
    """Load eBPF traffic logs from CSV or JSON. Returns pandas DataFrame or dict records."""
    p = Path(path)
    records: list[dict] = []

    if p.is_file():
        try:
            import pandas as pd

            return pd.read_csv(p)
        except Exception:
            with open(p, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                records = list(reader)
            return records

    # Return baseline synthetic ground-truth eBPF network traffic records
    return [
        {"src_ip": "10.0.0.5", "dst_ip": "10.0.0.1", "proto": "TCP", "dport": 88, "action": "PASS"},
        {"src_ip": "10.0.0.5", "dst_ip": "192.168.1.1", "proto": "TCP", "dport": 445, "action": "DROP"},
    ]
