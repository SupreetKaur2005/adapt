"""Tests for `adapt.routing.model_clients.hf_client`.

Mocks `transformers` via `sys.modules` so these run without the (heavy)
real dependency installed.
"""
import sys
import types


def test_generate_uses_lazily_built_pipeline(monkeypatch):
    calls = {}

    def fake_pipeline(task, model):
        calls["task"] = task
        calls["model"] = model

        def runner(prompt, **kwargs):
            return [{"generated_text": f"echo: {prompt}"}]

        return runner

    fake_module = types.ModuleType("transformers")
    fake_module.pipeline = fake_pipeline
    monkeypatch.setitem(sys.modules, "transformers", fake_module)

    from adapt.routing.model_clients.hf_client import HFClient

    client = HFClient("gpt2")
    result = client.generate("hello")

    assert result == "echo: hello"
    assert calls == {"task": "text-generation", "model": "gpt2"}


def test_pipeline_is_only_built_once(monkeypatch):
    build_count = {"n": 0}

    def fake_pipeline(task, model):
        build_count["n"] += 1

        def runner(prompt, **kwargs):
            return [{"generated_text": prompt}]

        return runner

    fake_module = types.ModuleType("transformers")
    fake_module.pipeline = fake_pipeline
    monkeypatch.setitem(sys.modules, "transformers", fake_module)

    from adapt.routing.model_clients.hf_client import HFClient

    client = HFClient("gpt2")
    client.generate("a")
    client.generate("b")

    assert build_count["n"] == 1
