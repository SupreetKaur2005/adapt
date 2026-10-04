"""Defines the simulated Active Directory domain (domain controller, user
accounts, Kerberos setup) that the AD-specific attack tools target.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ADLabConfig:
    domain_name: str = "adapt.lab"
    domain_controller: str = "dc01"
    user_accounts: list[str] = field(default_factory=list)
