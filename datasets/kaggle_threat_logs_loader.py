"""Loads the 6M+ row synthetic threat-log dataset.

Used to pretrain or sanity-check the Blue Team's classification behavior
before it ever sees live sandbox telemetry.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_threat_logs(path: Path | str) -> pd.DataFrame:
    raise NotImplementedError
