"""Loads the synthetic threat-log dataset.

Used to pretrain or sanity-check the Blue Team's classification behavior
before it ever sees live sandbox telemetry.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


def load_threat_logs(path: Path | str) -> Any:
    """Load threat logs from disk. Returns pandas DataFrame or dict records."""
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

    # Return baseline synthetic threat log records
    return [
        {"timestamp": "2026-10-04T12:00:00Z", "event_id": 4769, "user": "svc_admin", "status": "0x0", "label": "attack"},
        {"timestamp": "2026-10-04T12:01:00Z", "event_id": 4624, "user": "alice", "status": "0x0", "label": "benign"},
    ]
