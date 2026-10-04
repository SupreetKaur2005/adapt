"""Tests for `adapt.sandbox.mininet_topology`.

Mocks `mininet` via `sys.modules` so these run on a plain dev machine
without real Linux network namespaces.
"""
import sys
import types

import yaml


def _install_fake_mininet(monkeypatch, calls):
    class FakeMininet:
        def __init__(self, link=None):
            pass

        def addHost(self, name):
            calls["hosts"].append(name)
            return name

        def addLink(self, a, b):
            calls["links"].append((a, b))

        def start(self):
            calls["started"] = True

    net_module = types.ModuleType("mininet.net")
    net_module.Mininet = FakeMininet
    link_module = types.ModuleType("mininet.link")
    link_module.TCLink = object

    monkeypatch.setitem(sys.modules, "mininet", types.ModuleType("mininet"))
    monkeypatch.setitem(sys.modules, "mininet.net", net_module)
    monkeypatch.setitem(sys.modules, "mininet.link", link_module)


def test_build_topology_reads_config_and_builds_hosts_and_links(tmp_path, monkeypatch):
    calls = {"hosts": [], "links": [], "started": False}
    _install_fake_mininet(monkeypatch, calls)

    config_path = tmp_path / "topo.yaml"
    config_path.write_text(
        yaml.dump(
            {
                "hosts": [{"name": "dc01"}, {"name": "ws01"}],
                "links": [["dc01", "ws01"]],
            }
        ),
        encoding="utf-8",
    )

    from adapt.sandbox.mininet_topology import build_topology

    build_topology(config_path)

    assert calls["hosts"] == ["dc01", "ws01"]
    assert calls["links"] == [("dc01", "ws01")]
    assert calls["started"] is True
