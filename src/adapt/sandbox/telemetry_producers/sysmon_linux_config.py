"""Configuration for Microsoft's Sysmon-for-Linux, generating syscall-level
events (execve, ptrace, etc.) that `agents.blue_team.telemetry_ingest` reads.
"""
from __future__ import annotations

SYSMON_CONFIG_XML = """<Sysmon schemaversion="4.90">
  <EventFiltering>
    <!-- TODO: define rules for execve, ptrace, network connect events -->
  </EventFiltering>
</Sysmon>
"""
