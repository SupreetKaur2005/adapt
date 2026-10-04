"""Map task language onto the local, filtered ATT&CK skill space.

The mapper deliberately uses a small transparent lexical matcher. It needs no
network access or embedding model, and returns no techniques when evidence is
too weak instead of assigning an arbitrary technique.
"""
from __future__ import annotations

import re

from adapt.schemas import AttackTechnique

# A compact fallback taxonomy for the tactics enabled in
# config/mitre_attack_config.yaml. When the local STIX bundle is available,
# its records take precedence and enrich these descriptions.
_BUILTIN: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    ("T1558", "Steal or Forge Kerberos Tickets", "credential-access", ("kerberos", "ticket", "kerberoast", "as-rep", "roast", "spn")),
    ("T1003", "OS Credential Dumping", "credential-access", ("credential dump", "credential extraction", "dump credentials", "lsass", "ntds", "sam database", "nt hash", "password hash")),
    ("T1110", "Brute Force", "credential-access", ("brute force", "password spray", "password guessing", "credential stuffing")),
    ("T1021", "Remote Services", "lateral-movement", ("remote service", "smb", "winrm", "rdp", "psexec", "lateral movement", "remote execution")),
    ("T1550", "Use Alternate Authentication Material", "lateral-movement", ("pass the hash", "pass the ticket", "stolen token", "alternate authentication")),
    ("T1046", "Network Service Discovery", "discovery", ("port scan", "port scanning", "open ports", "service scan", "network service", "scan host")),
    ("T1018", "Remote System Discovery", "discovery", ("remote system", "discover hosts", "host discovery", "find computers", "network hosts")),
    ("T1087", "Account Discovery", "discovery", ("account discovery", "enumerate users", "list users", "user accounts", "domain accounts")),
    ("T1082", "System Information Discovery", "discovery", ("system information", "operating system", "os version", "system details")),
)

_TOKEN_RE = re.compile(r"[^a-z0-9]+")


def _normalize(text: str) -> str:
    return " ".join(_TOKEN_RE.sub(" ", text.lower()).split())


def _techniques() -> list[AttackTechnique]:
    """Load local STIX data if present, otherwise use the bundled core set."""
    from pathlib import Path

    from adapt.mitre.skill_space import SkillSpace

    records: list[AttackTechnique] = []
    bundle = Path(__file__).resolve().parents[3] / "data" / "raw_datasets" / "mitre" / "enterprise-attack.json"
    if bundle.is_file():
        try:
            from datasets.mitre_attack_loader import load_attack_techniques

            records = load_attack_techniques(bundle)
        except (ImportError, NotImplementedError, ValueError, OSError):
            records = []
    if not records:
        records = [AttackTechnique(technique_id=i, name=n, tactic=t, description=" ".join(k)) for i, n, t, k in _BUILTIN]
    return SkillSpace.from_config(records).techniques


def _score(text: str, technique: AttackTechnique) -> int:
    normalized = " " + _normalize(text) + " "
    score = 0
    for phrase in (technique.name, technique.technique_id, technique.description):
        phrase = _normalize(phrase)
        if len(phrase) >= 3 and f" {phrase} " in normalized:
            score += 2 if phrase == technique.name.lower() else 3
    for technique_id, _, _, keywords in _BUILTIN:
        if technique.technique_id == technique_id:
            score += sum(2 for keyword in keywords if f" {_normalize(keyword)} " in normalized)
            break
    return score


def map_to_technique(subtask: str) -> list[AttackTechnique]:
    """Return up to three relevant techniques ordered by lexical evidence."""
    if not isinstance(subtask, str):
        raise TypeError("subtask must be a string")
    if not subtask.strip():
        return []
    ranked = [(score, technique) for technique in _techniques() if (score := _score(subtask, technique)) > 0]
    ranked.sort(key=lambda item: (-item[0], item[1].technique_id))
    return [technique for _, technique in ranked[:3]]
