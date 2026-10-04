"""Shared sys.modules fakes for impacket's Kerberos internals, used by the
kerberoast/asrep_roast tool tests so they run without a live KDC.
"""
from __future__ import annotations

import sys
import types


def install_fake_kerberos(monkeypatch, decoded_payload, tgs_rep_bytes: bytes = b"tgs-rep-bytes"):
    calls: dict = {}

    class FakePrincipal:
        def __init__(self, value, type=None, default_realm=None):
            self.value = value
            self.type = type

    def fake_get_tgt(client_principal, password, domain, lmhash, nthash, aesKey, kdcHost, **kwargs):
        calls["tgt"] = {
            "principal": client_principal,
            "password": password,
            "domain": domain,
            "kdcHost": kdcHost,
            **kwargs,
        }
        return b"tgt-bytes", "cipher-obj", "key-obj", "session-key-obj"

    def fake_get_tgs(server_principal, domain, kdcHost, tgt, cipher, sessionKey, **kwargs):
        calls["tgs"] = {
            "principal": server_principal,
            "domain": domain,
            "kdcHost": kdcHost,
            "tgt": tgt,
            "cipher": cipher,
            "sessionKey": sessionKey,
        }
        return tgs_rep_bytes, "cipher2", "sk2", "nsk2"

    def fake_decode(data, asn1Spec=None):
        calls.setdefault("decoded_inputs", []).append(data)
        return decoded_payload, b""

    kerberosv5_mod = types.ModuleType("impacket.krb5.kerberosv5")
    kerberosv5_mod.getKerberosTGT = fake_get_tgt
    kerberosv5_mod.getKerberosTGS = fake_get_tgs

    constants_mod = types.ModuleType("impacket.krb5.constants")
    constants_mod.PrincipalNameType = types.SimpleNamespace(
        NT_PRINCIPAL=types.SimpleNamespace(value=1),
        NT_SRV_INST=types.SimpleNamespace(value=2),
    )

    asn1_mod = types.ModuleType("impacket.krb5.asn1")
    asn1_mod.TGS_REP = object
    asn1_mod.AS_REP = object

    types_mod = types.ModuleType("impacket.krb5.types")
    types_mod.Principal = FakePrincipal

    krb5_pkg = types.ModuleType("impacket.krb5")
    krb5_pkg.constants = constants_mod
    krb5_pkg.asn1 = asn1_mod
    krb5_pkg.kerberosv5 = kerberosv5_mod
    krb5_pkg.types = types_mod

    decoder_mod = types.ModuleType("pyasn1.codec.der.decoder")
    decoder_mod.decode = fake_decode
    der_pkg = types.ModuleType("pyasn1.codec.der")
    der_pkg.decoder = decoder_mod

    fakes = {
        "impacket.krb5": krb5_pkg,
        "impacket.krb5.constants": constants_mod,
        "impacket.krb5.asn1": asn1_mod,
        "impacket.krb5.kerberosv5": kerberosv5_mod,
        "impacket.krb5.types": types_mod,
        "pyasn1.codec.der": der_pkg,
        "pyasn1.codec.der.decoder": decoder_mod,
    }
    for name, mod in fakes.items():
        monkeypatch.setitem(sys.modules, name, mod)

    return calls
