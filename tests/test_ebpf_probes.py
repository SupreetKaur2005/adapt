"""Tests for sandbox/telemetry_producers/ebpf_probes/.

Covers:
  - probe_specs: metadata, filter rules alignment with sysmon_linux_config.py, C source reading
  - manager: Linux-awareness, lazy imports, safe mock mode, graceful fallback, event streaming
  - integration: live_stream hook and Blue Team telemetry ingestion compatibility

All tests are completely self-contained and run on Windows without eBPF, Linux kernel,
root privileges, Docker, or Mininet.
"""
from __future__ import annotations

import pytest

from adapt.sandbox.telemetry_producers import (
    get_active_producer,
    get_ebpf_manager,
    live_stream,
    set_active_producer,
)
from adapt.sandbox.telemetry_producers.ebpf_probes import (
    DEFAULT_PROBES,
    EBPFProbeManager,
    ProbeDefinition,
    get_probe_c_source,
    get_probe_definition,
    is_ebpf_available,
    is_linux,
    is_root,
    list_probe_names,
)
from adapt.schemas import TelemetryEvent


class TestProbeSpecs:
    """Verify probe definitions, C source availability, and rule alignment."""

    def test_default_probes_exist(self) -> None:
        names = list_probe_names()
        assert "process_exec" in names
        assert "network_connect" in names
        assert "process_access" in names
        assert len(names) >= 3

    def test_probe_definitions_fields(self) -> None:
        for name, probe in DEFAULT_PROBES.items():
            assert isinstance(probe, ProbeDefinition)
            assert probe.name == name
            assert len(probe.event_type) > 0
            assert len(probe.tracepoint) > 0
            assert len(probe.description) > 0
            assert probe.c_source_file.endswith(".bpf.c")

    def test_process_exec_filters_match_sysmon(self) -> None:
        probe = get_probe_definition("process_exec")
        assert probe is not None
        assert probe.event_type == "ProcessCreate"
        assert "/bin/sh" in probe.filter_rules["images"]
        assert "/bin/bash" in probe.filter_rules["images"]
        assert "mimikatz" in probe.filter_rules["command_line_keywords"]
        assert "kerberoast" in probe.filter_rules["command_line_keywords"]

    def test_network_connect_filters_match_sysmon(self) -> None:
        probe = get_probe_definition("network_connect")
        assert probe is not None
        assert probe.event_type == "NetworkConnect"
        ports = probe.filter_rules["destination_ports"]
        assert 88 in ports  # Kerberos
        assert 389 in ports  # LDAP
        assert 445 in ports  # SMB

    def test_process_access_filters_match_sysmon(self) -> None:
        probe = get_probe_definition("process_access")
        assert probe is not None
        assert probe.event_type == "ProcessAccess"
        assert "lsass" in probe.filter_rules["target_images"]
        assert "0x1400" in probe.filter_rules["granted_access"]

    def test_get_probe_definition_unknown(self) -> None:
        assert get_probe_definition("non_existent_probe") is None

    def test_get_c_source_valid(self) -> None:
        for name in ["process_exec", "network_connect", "process_access"]:
            c_src = get_probe_c_source(name)
            assert isinstance(c_src, str)
            assert len(c_src) > 50
            assert "BPF_PERF_OUTPUT" in c_src

    def test_get_c_source_unknown_raises(self) -> None:
        with pytest.raises(KeyError):
            get_probe_c_source("invalid_probe_id")


class TestManagerPlatformAndFallback:
    """Verify platform detection, fallback mechanics, and lazy loading."""

    def test_is_linux_returns_bool(self) -> None:
        assert isinstance(is_linux(), bool)

    def test_is_root_returns_bool(self) -> None:
        assert isinstance(is_root(), bool)

    def test_is_ebpf_available_returns_bool(self) -> None:
        assert isinstance(is_ebpf_available(), bool)

    def test_init_safe_mock_default_on_non_ebpf(self) -> None:
        # Should initialize gracefully without crashing
        mgr = EBPFProbeManager(mock=True)
        assert mgr.is_mock is True
        assert not mgr.is_running

    def test_init_graceful_fallback(self) -> None:
        # When mock=False on Windows, fallback_to_mock=True should keep it functional
        mgr = EBPFProbeManager(mock=False, fallback_to_mock=True)
        if not is_ebpf_available():
            assert mgr.is_mock is True

    def test_init_raises_without_fallback_on_unsupported_platform(self) -> None:
        if not is_ebpf_available():
            with pytest.raises(RuntimeError) as exc_info:
                EBPFProbeManager(mock=False, fallback_to_mock=False)
            assert "eBPF is not available" in str(exc_info.value)

    def test_get_ebpf_manager_helper(self) -> None:
        mgr = get_ebpf_manager(mock=True, host="10.0.0.99")
        assert mgr.host == "10.0.0.99"
        assert mgr.is_mock is True


class TestManagerLifecycleAndProbes:
    """Verify probe attachment, detachment, and running state."""

    def test_start_stop_lifecycle(self) -> None:
        mgr = EBPFProbeManager(mock=True)
        assert not mgr.is_running
        mgr.start()
        assert mgr.is_running
        mgr.stop()
        assert not mgr.is_running

    def test_context_manager(self) -> None:
        mgr = EBPFProbeManager(mock=True)
        with mgr:
            assert mgr.is_running
        assert not mgr.is_running

    def test_attach_and_detach_probe(self) -> None:
        mgr = EBPFProbeManager(mock=True, enabled_probes=["process_exec"])
        assert mgr.active_probes == {"process_exec"}

        assert mgr.attach_probe("network_connect") is True
        assert "network_connect" in mgr.active_probes

        assert mgr.attach_probe("invalid_probe") is False

        assert mgr.detach_probe("process_exec") is True
        assert "process_exec" not in mgr.active_probes

        assert mgr.detach_probe("process_exec") is False


class TestMockEventGeneration:
    """Verify deterministic mock events match schemas and sensor shapes."""

    def test_generate_mock_process_create(self) -> None:
        mgr = EBPFProbeManager(mock=True, host="10.0.0.10")
        event = mgr.generate_mock_event("ProcessCreate")
        assert isinstance(event, TelemetryEvent)
        assert event.source == "ebpf"
        assert event.host == "10.0.0.10"
        assert event.raw["event_type"] == "ProcessCreate"
        assert event.raw["syscall"] == "execve"
        assert event.raw["image"] == "/bin/sh"

    def test_generate_mock_network_connect(self) -> None:
        mgr = EBPFProbeManager(mock=True, host="ws01")
        event = mgr.generate_mock_event("NetworkConnect")
        assert event.source == "ebpf"
        assert event.host == "ws01"
        assert event.raw["event_type"] == "NetworkConnect"
        assert event.raw["destination_port"] == 88
        assert event.raw["protocol"] == "TCP"

    def test_generate_mock_process_access(self) -> None:
        mgr = EBPFProbeManager(mock=True)
        event = mgr.generate_mock_event("ProcessAccess")
        assert event.source == "ebpf"
        assert event.raw["event_type"] == "ProcessAccess"
        assert event.raw["target_image"] == "lsass"
        assert event.raw["granted_access"] == "0x1400"

    def test_generate_mock_batch(self) -> None:
        mgr = EBPFProbeManager(mock=True)
        batch = mgr.generate_mock_batch()
        assert len(batch) == 3
        types = {e.raw["event_type"] for e in batch}
        assert types == {"ProcessCreate", "NetworkConnect", "ProcessAccess"}

    def test_poll_and_stream_events(self) -> None:
        mgr = EBPFProbeManager(mock=True)
        mgr.generate_mock_batch()
        polled = mgr.poll_events(max_events=2)
        assert len(polled) == 2

        remaining = list(mgr.stream_events())
        assert len(remaining) == 1

        # Buffer now empty
        assert len(mgr.poll_events()) == 0


class TestBlueTeamIngestionIntegration:
    """Verify compatibility with Supreet's telemetry_ingest and live_stream."""

    def test_live_stream_empty_by_default(self) -> None:
        set_active_producer(None)
        assert list(live_stream()) == []

    def test_live_stream_with_active_producer(self) -> None:
        mgr = EBPFProbeManager(mock=True)
        mgr.start()
        mgr.generate_mock_event("ProcessCreate")
        mgr.generate_mock_event("NetworkConnect")
        set_active_producer(mgr)

        events = list(live_stream())
        assert len(events) == 2
        assert events[0].source == "ebpf"
        assert events[1].source == "ebpf"

        mgr.stop()
        set_active_producer(None)

    def test_ingest_events_integration(self) -> None:
        from adapt.agents.blue_team.telemetry_ingest import ingest_events
        from adapt.agents.blue_team.tools.telemetry_query_tool import (
            clear_telemetry,
            telemetry_query,
        )

        clear_telemetry()
        mgr = EBPFProbeManager(mock=True, host="10.0.0.5")
        mgr.start()
        mgr.generate_mock_event("ProcessCreate", custom_fields={"command_line": "mimikatz dump"})
        mgr.generate_mock_event("NetworkConnect", custom_fields={"destination_port": 88})
        set_active_producer(mgr)

        consumed = list(ingest_events())
        assert len(consumed) == 2
        assert consumed[0].source == "ebpf"

        # Check telemetry query tool recorded the events
        found_mimi = telemetry_query("mimikatz")
        assert len(found_mimi) >= 1
        found_kerb = telemetry_query("88")
        assert len(found_kerb) >= 1

        mgr.stop()
        set_active_producer(None)
        clear_telemetry()
