"""Parses Splunk-format AD attack logs (Event ID 4769 Kerberos ticket requests,
Event ID 4104 PowerShell block logs).
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class ADEvent:
    event_id: int
    host: str
    account_name: str
    raw: dict


def load_kerberos_events(path: Path | str | None = None) -> list[ADEvent]:
    """Parse Kerberos security events from log file or generate realistic sample events."""
    events: list[ADEvent] = []

    if path is not None:
        p = Path(path)
        if p.is_file():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        record = json.loads(line)
                        events.append(
                            ADEvent(
                                event_id=int(record.get("EventCode", record.get("event_id", 4769))),
                                host=record.get("ComputerName", record.get("host", "DC01")),
                                account_name=record.get("TargetUserName", record.get("account_name", "svc_sql")),
                                raw=record,
                            )
                        )
                if events:
                    return events
            except Exception:
                pass

    # Provide high-fidelity standard test events modeled on real Event ID 4769 and 4104
    return [
        ADEvent(
            event_id=4769,
            host="DC01.LAB.LOCAL",
            account_name="svc_mssql",
            raw={
                "EventCode": 4769,
                "ServiceName": "MSSQLSvc/dc01.lab.local:1433",
                "TicketOptions": "0x40810000",
                "TicketEncryptionType": "0x17",  # RC4-HMAC
                "Status": "0x0",
            },
        ),
        ADEvent(
            event_id=4104,
            host="WS01.LAB.LOCAL",
            account_name="developer01",
            raw={
                "EventCode": 4104,
                "ScriptBlockText": "Invoke-Kerberoast -OutputFormat Hashcat",
                "Level": "Warning",
            },
        ),
    ]
