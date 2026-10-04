"""Defines the simulated Active Directory domain (domain controller, user
accounts, Kerberos setup) that the AD-specific attack tools target.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ADAccount:
    username: str
    password: str
    spns: list[str] = field(default_factory=list)
    preauth_required: bool = True
    is_admin: bool = False


@dataclass
class ADLabConfig:
    domain_name: str = "adapt.lab"
    realm: str = "ADAPT.LAB"
    domain_controller: str = "dc01.adapt.lab"
    dc_ip: str = "10.0.1.10"
    user_accounts: list[ADAccount] = field(
        default_factory=lambda: [
            ADAccount(
                username="svc_mssql",
                password="Password123!",
                spns=["MSSQLSvc/dc01.adapt.lab:1433"],
                preauth_required=True,
            ),
            ADAccount(
                username="asrep_user",
                password="WeakPassword2026",
                spns=[],
                preauth_required=False,
            ),
            ADAccount(
                username="rodc_krbtgt",
                password="RODCKey123456",
                spns=[],
                preauth_required=True,
                is_admin=True,
            ),
        ]
    )
