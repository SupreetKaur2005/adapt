"""Kerberoasting attack tool (Event ID 4769-style), modeled on the patterns in
`datasets.splunk_ad_kerberos_loader`.
"""
from __future__ import annotations


def kerberoast(target_host: str, domain: str) -> dict:
    raise NotImplementedError
