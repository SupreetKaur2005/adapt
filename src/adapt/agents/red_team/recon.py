"""Scans the current sandbox target for open ports, services, and known entry points."""
from __future__ import annotations

import socket
from dataclasses import dataclass

# Ports relevant to the project's web/AD-lab targets. Keyed so results can
# name the service, not just the port number.
_SERVICE_NAMES: dict[int, str] = {
    21: "ftp",
    22: "ssh",
    23: "telnet",
    25: "smtp",
    53: "dns",
    80: "http",
    88: "kerberos",
    135: "msrpc",
    139: "netbios-ssn",
    389: "ldap",
    443: "https",
    445: "smb",
    464: "kpasswd",
    3389: "rdp",
}


@dataclass
class ReconResult:
    target_host: str
    open_ports: list[int]
    services: list[str]


def scan(
    target_host: str,
    ports: list[int] | None = None,
    timeout: float = 0.05,
) -> ReconResult:
    ports_to_check = ports if ports is not None else list(_SERVICE_NAMES)

    open_ports: list[int] = []
    services: list[str] = []
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            if sock.connect_ex((target_host, port)) == 0:
                open_ports.append(port)
                services.append(_SERVICE_NAMES.get(port, f"unknown-{port}"))
        except (OSError, socket.gaierror):
            pass
        finally:
            sock.close()

    return ReconResult(target_host=target_host, open_ports=open_ports, services=services)
