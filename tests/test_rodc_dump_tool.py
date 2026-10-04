"""Tests for `adapt.agents.red_team.tools.rodc_dump_tool`."""
import sys
import types

import pytest


def _install_fake_secretsdump(monkeypatch, secrets_to_emit):
    calls = {}

    class FakeSMBConnection:
        def __init__(self, remoteName, remoteHost):
            calls["smb_init"] = (remoteName, remoteHost)

        def login(self, user, password, domain):
            calls["login"] = (user, password, domain)

    class FakeRemoteOperations:
        def __init__(self, smb_connection, doKerberos, kdcHost):
            calls["remote_ops_init"] = (doKerberos, kdcHost)

        def getBootKey(self):
            return b"bootkey"

        def finish(self):
            calls["remote_ops_finished"] = True

    class FakeNTDSHashes:
        def __init__(self, ntdsFile, bootKey, isRemote=False, remoteOps=None, perSecretCallback=None):
            calls["ntds_init"] = (ntdsFile, bootKey, isRemote)
            self._callback = perSecretCallback

        def dump(self):
            for secret in secrets_to_emit:
                self._callback("NTLM", secret)

        def finish(self):
            calls["ntds_finished"] = True

    smb_mod = types.ModuleType("impacket.smbconnection")
    smb_mod.SMBConnection = FakeSMBConnection

    secretsdump_mod = types.ModuleType("impacket.examples.secretsdump")
    secretsdump_mod.RemoteOperations = FakeRemoteOperations
    secretsdump_mod.NTDSHashes = FakeNTDSHashes

    examples_pkg = types.ModuleType("impacket.examples")
    examples_pkg.secretsdump = secretsdump_mod

    monkeypatch.setitem(sys.modules, "impacket.smbconnection", smb_mod)
    monkeypatch.setitem(sys.modules, "impacket.examples", examples_pkg)
    monkeypatch.setitem(sys.modules, "impacket.examples.secretsdump", secretsdump_mod)

    return calls


def test_rodc_dump_requires_credentials():
    from adapt.agents.red_team.tools.rodc_dump_tool import rodc_dump

    with pytest.raises(ValueError):
        rodc_dump("dc01", "CORP.LOCAL")


def test_rodc_dump_collects_emitted_secrets(monkeypatch):
    calls = _install_fake_secretsdump(monkeypatch, ["jdoe:1001:aad3b435:cafebabe:::"])

    from adapt.agents.red_team.tools.rodc_dump_tool import rodc_dump

    result = rodc_dump("rodc01", "CORP.LOCAL", username="admin", password="pw")

    assert result == {
        "target_host": "rodc01",
        "domain": "CORP.LOCAL",
        "dumped_secrets": ["jdoe:1001:aad3b435:cafebabe:::"],
    }
    assert calls["login"] == ("admin", "pw", "CORP.LOCAL")
    assert calls["remote_ops_finished"] is True
    assert calls["ntds_finished"] is True
