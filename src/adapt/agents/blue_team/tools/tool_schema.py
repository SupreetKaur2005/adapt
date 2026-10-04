"""JSON-schema descriptions of every Blue Team tool -- mirrors the Red Team
tool pattern.
"""
from __future__ import annotations

BLUE_TEAM_TOOL_SCHEMAS: list[dict] = [
    {
        "name": "telemetry_query",
        "description": "Query ingested telemetry events by filter expression.",
        "parameters": {
            "type": "object",
            "properties": {"filter_expr": {"type": "string"}},
            "required": ["filter_expr"],
        },
    },
    {
        "name": "patch_deploy",
        "description": "Deploy a synthesized patch to a target host in the sandbox.",
        "parameters": {
            "type": "object",
            "properties": {
                "target_host": {"type": "string"},
                "patch_diff": {"type": "string"},
            },
            "required": ["target_host", "patch_diff"],
        },
    },
]
