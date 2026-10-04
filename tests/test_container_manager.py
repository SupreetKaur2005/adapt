"""Tests for `adapt.sandbox.container_manager`."""
from adapt.sandbox import container_manager


def test_start_calls_docker_compose_up(monkeypatch):
    calls = []
    monkeypatch.setattr(
        container_manager.subprocess, "run", lambda args, **kw: calls.append(list(args))
    )

    container_manager.start()

    assert calls[0][:2] == ["docker", "compose"]
    assert "up" in calls[0]


def test_reset_tears_down_then_brings_back_up(monkeypatch):
    calls = []
    monkeypatch.setattr(
        container_manager.subprocess, "run", lambda args, **kw: calls.append(list(args))
    )

    container_manager.reset()

    assert "down" in calls[0]
    assert "up" in calls[1]
