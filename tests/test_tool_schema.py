from __future__ import annotations

from adapt.agents.blue_team.tools.tool_schema import BLUE_TEAM_TOOL_SCHEMAS
from adapt.agents.red_team.tools.tool_schema import RED_TEAM_TOOL_SCHEMAS


def test_tool_schemas():
    assert len(RED_TEAM_TOOL_SCHEMAS) >= 5
    for schema in RED_TEAM_TOOL_SCHEMAS:
        assert "name" in schema
        assert "description" in schema
        assert "parameters" in schema
        assert schema["parameters"]["type"] == "object"
        assert "properties" in schema["parameters"]

    assert len(BLUE_TEAM_TOOL_SCHEMAS) >= 2
    for schema in BLUE_TEAM_TOOL_SCHEMAS:
        assert "name" in schema
        assert "description" in schema
        assert "parameters" in schema
        assert schema["parameters"]["type"] == "object"
        assert "properties" in schema["parameters"]
