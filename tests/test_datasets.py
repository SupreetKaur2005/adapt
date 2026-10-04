from __future__ import annotations

import tempfile
from pathlib import Path

from datasets.atomic_redteam_loader import load_playbooks
from datasets.ebpf_traffic_loader import load_ebpf_traffic
from datasets.impacket_trace_generator import generate_trace
from datasets.kaggle_threat_logs_loader import load_threat_logs
from datasets.mitre_attack_loader import load_attack_techniques
from datasets.splunk_ad_kerberos_loader import load_kerberos_events


def test_atomic_redteam_loader():
    playbooks = load_playbooks("T1558")
    assert len(playbooks) >= 1
    assert playbooks[0].technique_id == "T1558"
    assert "kerberoast" in playbooks[0].name.lower() or "powershell" in playbooks[0].command.lower()


def test_mitre_attack_loader():
    # Test on empty or non-existent bundle path returns gracefully
    techniques = load_attack_techniques("non_existent_bundle.json")
    assert isinstance(techniques, list)
    assert len(techniques) == 0


def test_splunk_ad_kerberos_loader():
    events = load_kerberos_events()
    assert len(events) >= 2
    assert any(e.event_id == 4769 for e in events)


def test_impacket_trace_generator():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_pcap = Path(tmpdir) / "test_attack.pcap"
        res_path = generate_trace("kerberoast", "dc01", output_path=out_pcap)
        assert res_path.exists()
        assert res_path.stat().st_size > 30


def test_ebpf_traffic_loader():
    traffic = load_ebpf_traffic("non_existent.csv")
    assert len(traffic) >= 1


def test_kaggle_threat_logs_loader():
    logs = load_threat_logs("non_existent.csv")
    assert len(logs) >= 1
