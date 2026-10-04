"""Loads the MITRE ATT&CK STIX bundle into AttackTechnique objects."""
from __future__ import annotations

import json
from pathlib import Path

from adapt.schemas import AttackTechnique


def load_attack_techniques(bundle_path: Path | str) -> list[AttackTechnique]:
    """Parse a STIX 2.1 or Enterprise ATT&CK bundle into AttackTechnique objects."""
    path = Path(bundle_path)
    if not path.is_file():
        return []

    techniques: list[AttackTechnique] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        objects = data.get("objects", []) if isinstance(data, dict) else []
        for obj in objects:
            if obj.get("type") != "attack-pattern":
                continue

            technique_id = None
            for ref in obj.get("external_references", []):
                if ref.get("source_name") in {"mitre-attack", "mitre-enterprise-attack"}:
                    technique_id = ref.get("external_id")
                    break

            if not technique_id:
                continue

            tactic = "unknown"
            kill_chains = obj.get("kill_chain_phases", [])
            if kill_chains:
                tactic = kill_chains[0].get("phase_name", "unknown")

            techniques.append(
                AttackTechnique(
                    technique_id=technique_id,
                    name=obj.get("name", "Unknown Technique"),
                    tactic=tactic,
                    description=obj.get("description", ""),
                )
            )
    except Exception:
        return []

    return techniques
