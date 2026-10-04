"""JSON-schema descriptions of every Red Team tool, passed to the local
model's function-calling interface.
"""
from __future__ import annotations

RED_TEAM_TOOL_SCHEMAS: list[dict] = [
    {
        "name": "port_scan",
        "description": "Scan a target host for open ports and services.",
        "parameters": {
            "type": "object",
            "properties": {"target_host": {"type": "string"}},
            "required": ["target_host"],
        },
    },
    {
        "name": "payload_execute",
        "description": "Execute a payload against a sandbox target.",
        "parameters": {
            "type": "object",
            "properties": {
                "target_host": {"type": "string"},
                "payload": {"type": "string"},
            },
            "required": ["target_host", "payload"],
        },
    },
    {
        "name": "kerberoast",
        "description": (
            "Attempt a Kerberoasting attack (Event ID 4769) against an AD domain: requests a "
            "service ticket for `spn` using already-obtained credentials and returns the "
            "crackable, encrypted part of that ticket."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "target_host": {"type": "string"},
                "domain": {"type": "string"},
                "username": {"type": "string"},
                "password": {"type": "string"},
                "spn": {"type": "string", "description": "Target service principal name."},
            },
            "required": ["target_host", "domain", "username", "password", "spn"],
        },
    },
    {
        "name": "asrep_roast",
        "description": (
            "Attempt an AS-REP roasting attack against an AD domain: requests a TGT with "
            "Kerberos pre-authentication disabled for `username` and returns the crackable, "
            "encrypted part of the AS-REP."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "target_host": {"type": "string"},
                "domain": {"type": "string"},
                "username": {"type": "string"},
            },
            "required": ["target_host", "domain", "username"],
        },
    },
    {
        "name": "rodc_dump",
        "description": "Attempt RODC credential dumping against a target host.",
        "parameters": {
            "type": "object",
            "properties": {
                "target_host": {"type": "string"},
                "domain": {"type": "string"},
                "username": {"type": "string"},
                "password": {"type": "string"},
            },
            "required": ["target_host", "domain", "username", "password"],
        },
    },
]
