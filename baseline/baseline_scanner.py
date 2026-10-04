"""Wraps a traditional (non-agentic) vulnerability scanner over the sandbox targets."""
from __future__ import annotations

from adapt.agents.red_team.recon import scan


def run_baseline_scanner(target_host: str, ports: list[int] | None = None) -> dict:
    """Run standard network and port banner scanner against target."""
    recon = scan(target_host, ports=ports)
    findings = []
    for port, service in zip(recon.open_ports, recon.services):
        findings.append(
            {
                "port": port,
                "service": service,
                "vulnerability": f"Potential service misconfiguration or credential exposure on {service}",
                "severity": "HIGH" if port in {88, 445, 3389} else "MEDIUM",
            }
        )

    return {
        "target_host": target_host,
        "open_ports": recon.open_ports,
        "findings_count": len(findings),
        "findings": findings,
    }
