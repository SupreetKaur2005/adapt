"""Tests for `adapt.agents.red_team.tools.port_scan_tool`."""
from adapt.agents.red_team.recon import ReconResult
from adapt.agents.red_team.tools import port_scan_tool
from adapt.agents.red_team.tools.port_scan_tool import port_scan


def test_port_scan_tool_wraps_recon_result(monkeypatch):
    # port_scan_tool imported `scan` with `from ... import scan`, so the name
    # to patch lives in port_scan_tool's own namespace, not recon's.
    monkeypatch.setattr(
        port_scan_tool,
        "scan",
        lambda target_host, ports=None, timeout=0.5: ReconResult(
            target_host=target_host, open_ports=[445], services=["smb"]
        ),
    )

    result = port_scan("dc01")

    assert result == {"target_host": "dc01", "open_ports": [445], "services": ["smb"]}
