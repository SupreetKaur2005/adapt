"""Per-agent, per-tier prompt templates.

Smaller local models generally need more explicit, structured prompting than
a frontier model would -- this is where that gets compensated for.
"""
from __future__ import annotations

RED_TEAM_TEMPLATES: dict[str, str] = {
    "lightweight": "",
    "mid": "",
    "heavy": "",
}

BLUE_TEAM_TEMPLATES: dict[str, str] = {
    "lightweight": "",
    "mid": "",
    "heavy": "",
}
