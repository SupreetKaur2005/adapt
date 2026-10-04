"""Tests for explicit Red and Blue outcome evidence."""
from adapt.verification.outcome_classifier import classify_blue_outcome, classify_red_outcome


def test_red_success_requires_positive_action_or_telemetry_evidence():
    assert classify_red_outcome([], []) is False
    assert classify_red_outcome([{"tool": "port_scan", "result": {"success": True}}], []) is False
    assert classify_red_outcome([{"result": {"exploit_success": True}}], []) is True
    assert classify_red_outcome([], [{"event_type": "exploit_success"}]) is True


def test_blue_success_recognizes_block_or_remediation():
    assert classify_blue_outcome([], []) is False
    assert classify_blue_outcome([{"tool": "telemetry_query", "result": {"success": True}}], []) is False
    assert classify_blue_outcome([{"result": {"patch_applied": True}}], []) is True
    assert classify_blue_outcome([], [{"event_name": "attack_detected"}]) is True
