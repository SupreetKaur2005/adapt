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


def test_resolve_app_finds_known_app_image_and_port():
    app = container_manager.resolve_app("vuln-web-sqli")
    assert app is not None
    assert app.docker_image == "adapt/vuln-web-sqli:latest"
    assert app.listen_port == 8080

    cmdi = container_manager.get_app("vuln-web-cmdi")
    assert cmdi is not None
    assert cmdi.docker_image == "adapt/vuln-web-cmdi:latest"
    assert cmdi.listen_port == 8081

    unknown = container_manager.resolve_app("nonexistent")
    assert unknown is None


def test_start_app_calls_docker_compose_for_specific_app(monkeypatch):
    calls = []
    monkeypatch.setattr(
        container_manager.subprocess, "run", lambda args, **kw: calls.append(list(args))
    )

    app = container_manager.start_app("vuln-web-sqli")
    assert app.app_id == "vuln-web-sqli"
    assert len(calls) == 1
    assert calls[0][:2] == ["docker", "compose"]
    assert "up" in calls[0]
    assert "vuln-web-sqli" in calls[0]
