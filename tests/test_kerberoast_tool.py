"""Tests for `adapt.agents.red_team.tools.kerberoast_tool`."""
import pytest

from tests._impacket_fakes import install_fake_kerberos


def test_kerberoast_requires_credentials():
    from adapt.agents.red_team.tools.kerberoast_tool import kerberoast

    with pytest.raises(ValueError):
        kerberoast("dc01", "CORP.LOCAL")


def test_kerberoast_returns_ticket_cipher(monkeypatch):
    decoded_payload = {"ticket": {"enc-part": {"etype": 23, "cipher": b"\xde\xad\xbe\xef"}}}
    calls = install_fake_kerberos(monkeypatch, decoded_payload)

    from adapt.agents.red_team.tools.kerberoast_tool import kerberoast

    result = kerberoast(
        "dc01", "CORP.LOCAL", username="svc_sql", password="pw", spn="MSSQLSvc/dc01:1433"
    )

    assert result == {
        "target_host": "dc01",
        "domain": "CORP.LOCAL",
        "spn": "MSSQLSvc/dc01:1433",
        "etype": 23,
        "ticket_cipher_hex": "deadbeef",
    }
    assert calls["tgt"]["domain"] == "CORP.LOCAL"
    assert calls["tgt"]["kdcHost"] == "dc01"
    assert calls["tgs"]["domain"] == "CORP.LOCAL"
