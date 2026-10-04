"""Generates a YARA detection rule from the same breach event, for future
prevention (distinct output from the patch itself).
"""
from __future__ import annotations


def generate_yara_rule(breach: dict) -> str:
    raise NotImplementedError
