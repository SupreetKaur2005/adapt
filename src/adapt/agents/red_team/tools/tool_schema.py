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
        "description": "Attempt a Kerberoasting attack (Event ID 4769) against an AD domain.",
        "parameters": {
            "type": "object",
            "properties": {
                "target_host": {"type": "string"},
                "domain": {"type": "string"},
            },
            "required": ["target_host", "domain"],
        },
    },
    {
        "name": "asrep_roast",
        "description": "Attempt an AS-REP roasting attack against an AD domain.",
        "parameters": {
            "type": "object",
            "properties": {
                "target_host": {"type": "string"},
                "domain": {"type": "string"},
            },
            "required": ["target_host", "domain"],
        },
    },
    {
        "name": "rodc_dump",
        "description": "Attempt RODC credential dumping against a target host.",
        "parameters": {
            "type": "object",
            "properties": {"target_host": {"type": "string"}},
            "required": ["target_host"],
        },
    },
]
