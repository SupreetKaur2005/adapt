"""Tests for `adapt.agents.red_team.recon`."""
from adapt.agents.red_team.recon import scan


class _FakeSocket:
    _open = {("10.0.0.5", 445), ("10.0.0.5", 80)}

    def __init__(self, *args, **kwargs):
        self._target = None

    def settimeout(self, timeout):
        pass

    def connect_ex(self, addr):
        self._target = addr
        return 0 if addr in self._open else 1

    def close(self):
        pass


def test_scan_reports_open_ports_and_services(monkeypatch):
    import socket

    monkeypatch.setattr(socket, "socket", lambda *a, **kw: _FakeSocket())

    result = scan("10.0.0.5", ports=[80, 445, 22])

    assert result.target_host == "10.0.0.5"
    assert set(result.open_ports) == {80, 445}
    assert set(result.services) == {"http", "smb"}


def test_scan_returns_empty_when_nothing_open(monkeypatch):
    import socket

    class _AllClosedSocket(_FakeSocket):
        def connect_ex(self, addr):
            return 1

    monkeypatch.setattr(socket, "socket", lambda *a, **kw: _AllClosedSocket())

    result = scan("10.0.0.9", ports=[22, 23])

    assert result.open_ports == []
    assert result.services == []


def test_scan_handles_unresolvable_host_gracefully():
    # Attempting to scan an invalid or unresolvable hostname should not raise an exception
    result = scan("invalid-host-name-that-does-not-exist.invalid", ports=[80], timeout=0.1)
    assert result.target_host == "invalid-host-name-that-does-not-exist.invalid"
    assert result.open_ports == []
    assert result.services == []
