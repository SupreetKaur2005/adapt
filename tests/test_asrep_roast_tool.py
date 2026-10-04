"""Tests for `adapt.agents.red_team.tools.asrep_roast_tool`."""
import pytest

from tests._impacket_fakes import install_fake_kerberos


def test_asrep_roast_requires_username():
    from adapt.agents.red_team.tools.asrep_roast_tool import asrep_roast

    with pytest.raises(ValueError):
        asrep_roast("dc01", "CORP.LOCAL")


def test_asrep_roast_returns_as_rep_cipher(monkeypatch):
    decoded_payload = {"enc-part": {"etype": 23, "cipher": b"\xca\xfe"}}
    calls = install_fake_kerberos(monkeypatch, decoded_payload)

    from adapt.agents.red_team.tools.asrep_roast_tool import asrep_roast

    result = asrep_roast("dc01", "CORP.LOCAL", username="jdoe")

    assert result == {
        "target_host": "dc01",
        "domain": "CORP.LOCAL",
        "username": "jdoe",
        "etype": 23,
        "as_rep_cipher_hex": "cafe",
    }
    assert calls["tgt"]["kdcHost"] == "dc01"
    assert calls["tgt"]["kerberoast_no_preauth"] is True
