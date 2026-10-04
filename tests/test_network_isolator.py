from __future__ import annotations

import pytest

from adapt.sandbox.network_isolator import is_sealed, seal_network, unseal_network


def test_network_isolator_lifecycle():
    ns = "adapt-sandbox-net"
    assert not is_sealed(ns)

    assert seal_network(ns) is True
    assert is_sealed(ns) is True

    assert unseal_network(ns) is True
    assert is_sealed(ns) is False


def test_network_isolator_invalid_namespace():
    with pytest.raises(ValueError):
        seal_network("")

    with pytest.raises(ValueError):
        seal_network(None)  # type: ignore
