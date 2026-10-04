"""Configuration for Microsoft's Sysmon-for-Linux, generating syscall-level
events (execve, ptrace, etc.) that `agents.blue_team.telemetry_ingest` reads.
"""
from __future__ import annotations

SYSMON_CONFIG_XML = """<Sysmon schemaversion="4.90">
  <EventFiltering>
    <RuleGroup name="ADAPT-BlueTeam-Sensors" groupRelation="or">
      <ProcessCreate onmatch="include">
        <Rule name="SuspiciousShellExecution" groupRelation="or">
          <Image condition="end with">/bin/sh</Image>
          <Image condition="end with">/bin/bash</Image>
          <Image condition="end with">powershell</Image>
          <Image condition="end with">pwsh</Image>
          <CommandLine condition="contains">kerberoast</CommandLine>
          <CommandLine condition="contains">mimikatz</CommandLine>
        </Rule>
      </ProcessCreate>
      <NetworkConnect onmatch="include">
        <Rule name="KerberosAndSMBTraffic" groupRelation="or">
          <DestinationPort condition="is">88</DestinationPort>
          <DestinationPort condition="is">389</DestinationPort>
          <DestinationPort condition="is">445</DestinationPort>
        </Rule>
      </NetworkConnect>
      <ProcessAccess onmatch="include">
        <Rule name="CredentialDumpingPtrace" groupRelation="or">
          <TargetImage condition="contains">lsass</TargetImage>
          <GrantedAccess condition="contains">0x1400</GrantedAccess>
        </Rule>
      </ProcessAccess>
    </RuleGroup>
  </EventFiltering>
</Sysmon>
"""
