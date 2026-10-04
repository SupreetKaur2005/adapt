"""Builds the Mininet network fabric the AD lab and Impacket traces run over.

`mininet` only runs on Linux (it needs real network namespaces), so it's
imported lazily inside `build_topology` -- this module stays importable
everywhere else, and callers on Linux get the real network.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parents[3] / "config" / "sandbox_topology.yaml"
)


def build_topology(config_path: Path | str = _DEFAULT_CONFIG_PATH) -> Any:
    """config: config/sandbox_topology.yaml -> a started Mininet `Network`."""
    from mininet.link import TCLink
    from mininet.net import Mininet

    with Path(config_path).open(encoding="utf-8") as f:
        topo_cfg = yaml.safe_load(f)

    net = Mininet(link=TCLink)
    hosts = {host_cfg["name"]: net.addHost(host_cfg["name"]) for host_cfg in topo_cfg["hosts"]}
    for host_a, host_b in topo_cfg["links"]:
        net.addLink(hosts[host_a], hosts[host_b])

    net.start()
    return net
