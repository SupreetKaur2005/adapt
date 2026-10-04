"""Tests for `adapt.routing.model_clients.ollama_client`.

Mocks the `ollama` package via `sys.modules` so these run without a live
Ollama server.
"""
import sys
import types


def _install_fake_ollama(monkeypatch, calls):
    class FakeOllamaClient:
        def __init__(self, host):
            calls["host"] = host

        def generate(self, model, prompt, **kwargs):
            calls["generate"] = (model, prompt, kwargs)
            return {"response": "Thought: ok\nAction: port_scan\nAction Input: {}"}

        def chat(self, model, messages, **kwargs):
            calls["chat"] = (model, messages, kwargs)
            return {"message": {"content": "hi"}}

    fake_module = types.ModuleType("ollama")
    fake_module.Client = FakeOllamaClient
    monkeypatch.setitem(sys.modules, "ollama", fake_module)


def test_generate_returns_response_text(monkeypatch):
    calls = {}
    _install_fake_ollama(monkeypatch, calls)

    from adapt.routing.model_clients.ollama_client import OllamaClient

    client = OllamaClient(host="http://test:1234")
    result = client.generate("mistral:7b", "do something")

    assert "Action: port_scan" in result
    assert calls["host"] == "http://test:1234"
    assert calls["generate"][0] == "mistral:7b"


def test_chat_returns_raw_response_dict(monkeypatch):
    calls = {}
    _install_fake_ollama(monkeypatch, calls)

    from adapt.routing.model_clients.ollama_client import OllamaClient

    client = OllamaClient()
    result = client.chat("mistral:7b", [{"role": "user", "content": "hi"}])

    assert result == {"message": {"content": "hi"}}
