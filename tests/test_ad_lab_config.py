"""Unit tests for adapt.sandbox.targets.ad_lab_config.

Covers:
  - Default AD domain configuration (domain_name, realm, DC name, DC IP)
  - Account definitions and attributes for all default simulated targets:
      * svc_mssql (Kerberoasting target with registered SPN)
      * asrep_user (AS-REP roasting target with preauth disabled)
      * rodc_krbtgt (RODC Golden Ticket target with admin privileges)
  - SPN format validation
  - Custom ADAccount and ADLabConfig construction
"""
from __future__ import annotations

import re

from adapt.sandbox.targets.ad_lab_config import ADAccount, ADLabConfig


class TestADLabConfigDefaults:
    """Verify default domain layout and service configuration."""

    def test_default_domain_parameters(self) -> None:
        cfg = ADLabConfig()
        assert cfg.domain_name == "adapt.lab"
        assert cfg.realm == "ADAPT.LAB"
        assert cfg.domain_controller == "dc01.adapt.lab"
        assert cfg.dc_ip == "10.0.1.10"
        assert len(cfg.user_accounts) == 3

    def test_accounts_by_username_mapping(self) -> None:
        cfg = ADLabConfig()
        accounts = {acc.username: acc for acc in cfg.user_accounts}
        assert "svc_mssql" in accounts
        assert "asrep_user" in accounts
        assert "rodc_krbtgt" in accounts


class TestDefaultTargetAccounts:
    """Verify credentials, SPNs, and security settings for default simulated accounts."""

    def test_svc_mssql_kerberoasting_target(self) -> None:
        cfg = ADLabConfig()
        acc = next(a for a in cfg.user_accounts if a.username == "svc_mssql")
        assert acc.username == "svc_mssql"
        assert acc.password == "Password123!"
        assert acc.preauth_required is True
        assert acc.is_admin is False
        assert len(acc.spns) == 1
        assert acc.spns[0] == "MSSQLSvc/dc01.adapt.lab:1433"

    def test_spn_format(self) -> None:
        cfg = ADLabConfig()
        acc = next(a for a in cfg.user_accounts if a.username == "svc_mssql")
        spn_pattern = re.compile(r"^[A-Za-z0-9_]+/[A-Za-z0-9_.-]+(:\d+)?$")
        for spn in acc.spns:
            assert spn_pattern.match(spn), f"SPN {spn!r} did not match expected format"

    def test_asrep_user_asrep_roasting_target(self) -> None:
        cfg = ADLabConfig()
        acc = next(a for a in cfg.user_accounts if a.username == "asrep_user")
        assert acc.username == "asrep_user"
        assert acc.password == "WeakPassword2026"
        assert acc.preauth_required is False
        assert acc.is_admin is False
        assert acc.spns == []

    def test_rodc_krbtgt_admin_target(self) -> None:
        cfg = ADLabConfig()
        acc = next(a for a in cfg.user_accounts if a.username == "rodc_krbtgt")
        assert acc.username == "rodc_krbtgt"
        assert acc.password == "RODCKey123456"
        assert acc.preauth_required is True
        assert acc.is_admin is True
        assert acc.spns == []


class TestCustomConstruction:
    """Verify custom ADAccount and ADLabConfig instances can be constructed cleanly."""

    def test_custom_account(self) -> None:
        acc = ADAccount(
            username="analyst_test",
            password="SecurePass2026!",
            spns=["HTTP/web01.adapt.lab:80"],
            preauth_required=True,
            is_admin=True,
        )
        assert acc.username == "analyst_test"
        assert acc.password == "SecurePass2026!"
        assert acc.spns == ["HTTP/web01.adapt.lab:80"]
        assert acc.preauth_required is True
        assert acc.is_admin is True

    def test_custom_lab_config(self) -> None:
        custom_acc = ADAccount(
            username="lab_user",
            password="LabUserPassword",
        )
        cfg = ADLabConfig(
            domain_name="test.corp",
            realm="TEST.CORP",
            domain_controller="dc.test.corp",
            dc_ip="192.168.10.5",
            user_accounts=[custom_acc],
        )
        assert cfg.domain_name == "test.corp"
        assert cfg.realm == "TEST.CORP"
        assert cfg.domain_controller == "dc.test.corp"
        assert cfg.dc_ip == "192.168.10.5"
        assert len(cfg.user_accounts) == 1
        assert cfg.user_accounts[0].username == "lab_user"
