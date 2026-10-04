"""Tests for local ATT&CK technique mapping."""
import pytest

from adapt.mitre.attack_mapper import map_to_technique


def test_maps_credential_extraction_to_kerberos_technique():
    techniques = map_to_technique("attempt Kerberos credential extraction with kerberoast against DC01")
    assert techniques
    assert techniques[0].technique_id == "T1558"


def test_maps_port_scan_to_network_service_discovery():
    assert map_to_technique("scan WS01 for open ports")[0].technique_id == "T1046"


def test_unmatched_text_returns_no_arbitrary_technique():
    assert map_to_technique("summarize this paragraph") == []


def test_invalid_input_is_rejected():
    with pytest.raises(TypeError):
        map_to_technique(None)
