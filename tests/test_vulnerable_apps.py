"""Tests for sandbox/targets/vulnerable_apps/.

Covers:
  - registry:     VulnerableApp data model, look-up functions, integrity checks
  - sim_server:   in-process HTTP server for both vulnerability surfaces

All tests are self-contained: no Docker, no network access beyond 127.0.0.1,
no root privileges, no GPU.
"""
from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request

import pytest

from adapt.sandbox.targets.vulnerable_apps.registry import (
    VULNERABLE_APPS,
    VulnerableApp,
    get_app,
    list_app_ids,
)
from adapt.sandbox.targets.vulnerable_apps.sim_server import VulnerableAppServer


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------

class TestRegistry:
    def test_registry_not_empty(self):
        assert len(VULNERABLE_APPS) >= 2

    def test_all_entries_are_vulnerable_app(self):
        for app in VULNERABLE_APPS:
            assert isinstance(app, VulnerableApp)

    def test_required_fields_non_empty(self):
        for app in VULNERABLE_APPS:
            assert app.app_id, f"app_id empty for {app}"
            assert app.display_name, f"display_name empty for {app}"
            assert app.cve_ref, f"cve_ref empty for {app}"
            assert app.description, f"description empty for {app}"
            assert app.attack_surface.startswith("/"), (
                f"attack_surface must start with '/' for {app.app_id}"
            )
            assert app.injectable_param, f"injectable_param empty for {app}"
            assert app.docker_image, f"docker_image empty for {app}"
            assert isinstance(app.listen_port, int) and app.listen_port > 0

    def test_unique_app_ids(self):
        ids = [app.app_id for app in VULNERABLE_APPS]
        assert len(ids) == len(set(ids)), "Duplicate app_ids found"

    def test_unique_ports(self):
        ports = [app.listen_port for app in VULNERABLE_APPS]
        assert len(ports) == len(set(ports)), "Duplicate listen_ports found"

    def test_get_app_known(self):
        app = get_app("vuln-web-sqli")
        assert app is not None
        assert app.app_id == "vuln-web-sqli"
        assert app.listen_port == 8080
        assert app.attack_surface == "/login"
        assert app.injectable_param == "user"

    def test_get_app_cmdi(self):
        app = get_app("vuln-web-cmdi")
        assert app is not None
        assert app.app_id == "vuln-web-cmdi"
        assert app.listen_port == 8081
        assert app.attack_surface == "/ping"
        assert app.injectable_param == "host"

    def test_get_app_unknown_returns_none(self):
        assert get_app("does-not-exist") is None

    def test_list_app_ids(self):
        ids = list_app_ids()
        assert "vuln-web-sqli" in ids
        assert "vuln-web-cmdi" in ids

    def test_known_payloads_present(self):
        app = get_app("vuln-web-sqli")
        assert len(app.known_payloads) >= 1
        assert any("OR" in p for p in app.known_payloads)

    def test_apps_in_scope_by_default(self):
        for app in VULNERABLE_APPS:
            assert app.in_scope_by_default is True


# ---------------------------------------------------------------------------
# Simulation server — registry
# ---------------------------------------------------------------------------

class TestVulnerableAppServerInit:
    def test_bad_app_type_raises(self):
        with pytest.raises(ValueError, match="Unknown app_type"):
            VulnerableAppServer("invalid-type")

    def test_url_format(self):
        srv = VulnerableAppServer("sqli", port=19999)
        assert srv.url == "http://127.0.0.1:19999"
        assert srv.host == "127.0.0.1"
        assert srv.port == 19999

    def test_auto_port_selection(self):
        srv = VulnerableAppServer("cmdi")
        assert srv.port > 0


# ---------------------------------------------------------------------------
# Simulation server — SQL injection surface (/login)
# ---------------------------------------------------------------------------

class TestSQLiSimServer:
    def _get(self, srv: VulnerableAppServer, path: str) -> tuple[int, str]:
        try:
            with urllib.request.urlopen(srv.url + path, timeout=5) as resp:
                return resp.status, resp.read().decode()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode()

    def test_health_endpoint(self):
        with VulnerableAppServer("sqli") as srv:
            code, body = self._get(srv, "/health")
            assert code == 200
            assert "OK" in body

    def test_valid_login(self):
        with VulnerableAppServer("sqli") as srv:
            code, body = self._get(srv, "/login?user=admin")
            assert code == 200
            assert "Welcome admin" in body

    def test_invalid_login(self):
        with VulnerableAppServer("sqli") as srv:
            code, body = self._get(srv, "/login?user=nobody")
            assert code == 401
            assert "FAIL" in body

    def test_sqli_bypass_or(self):
        """' OR '1'='1 should bypass authentication."""
        with VulnerableAppServer("sqli") as srv:
            payload = urllib.parse.quote("' OR '1'='1")
            code, body = self._get(srv, f"/login?user={payload}")
            assert code == 200
            assert "SQLI" in body
            assert "bypassed" in body

    def test_sqli_bypass_union(self):
        with VulnerableAppServer("sqli") as srv:
            payload = urllib.parse.quote("' UNION SELECT password FROM users--")
            code, body = self._get(srv, f"/login?user={payload}")
            assert code == 200
            assert "SQLI" in body

    def test_sqli_comment_bypass(self):
        with VulnerableAppServer("sqli") as srv:
            payload = urllib.parse.quote("admin'--")
            code, body = self._get(srv, f"/login?user={payload}")
            # admin' stripped to admin -> normal login path
            assert code == 200

    def test_unknown_path_404(self):
        with VulnerableAppServer("sqli") as srv:
            code, _ = self._get(srv, "/does-not-exist")
            assert code == 404

    def test_context_manager_cleans_up(self):
        """Server should not accept connections after __exit__."""
        srv = VulnerableAppServer("sqli")
        with srv:
            code, _ = self._get(srv, "/health")
            assert code == 200
        # After exit, server is stopped — no assertion, just ensure no hang/exception.
        assert srv._server is None

    def test_start_idempotent(self):
        """Calling start() twice must not raise."""
        with VulnerableAppServer("sqli") as srv:
            srv.start()   # second call — should be a no-op
            code, _ = self._get(srv, "/health")
            assert code == 200


# ---------------------------------------------------------------------------
# Simulation server — command injection surface (/ping)
# ---------------------------------------------------------------------------

class TestCMDiSimServer:
    def _get(self, srv: VulnerableAppServer, path: str) -> tuple[int, str]:
        try:
            with urllib.request.urlopen(srv.url + path, timeout=5) as resp:
                return resp.status, resp.read().decode()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode()

    def test_clean_ping(self):
        with VulnerableAppServer("cmdi") as srv:
            code, body = self._get(srv, "/ping?host=127.0.0.1")
            assert code == 200
            assert "PING" in body
            assert "127.0.0.1" in body

    def test_cmdi_semicolon_id(self):
        """127.0.0.1; id  → simulated id output."""
        with VulnerableAppServer("cmdi") as srv:
            payload = urllib.parse.quote("127.0.0.1; id")
            code, body = self._get(srv, f"/ping?host={payload}")
            assert code == 200
            assert "CMDI" in body
            assert "uid=0(root)" in body

    def test_cmdi_ampersand_whoami(self):
        with VulnerableAppServer("cmdi") as srv:
            payload = urllib.parse.quote("127.0.0.1 && whoami")
            code, body = self._get(srv, f"/ping?host={payload}")
            assert code == 200
            assert "CMDI" in body

    def test_cmdi_backtick(self):
        with VulnerableAppServer("cmdi") as srv:
            payload = urllib.parse.quote("$(whoami)")
            code, body = self._get(srv, f"/ping?host={payload}")
            assert code == 200
            assert "CMDI" in body

    def test_cmdi_unknown_command_still_responds(self):
        """Unknown injected command → generic simulated output, not a crash."""
        with VulnerableAppServer("cmdi") as srv:
            payload = urllib.parse.quote("127.0.0.1; totally_unknown_cmd_xyz")
            code, body = self._get(srv, f"/ping?host={payload}")
            assert code == 200
            assert "CMDI" in body
            assert "simulated output" in body

    def test_no_real_shell_execution(self):
        """Verify no real shell commands run: real 'id' output won't contain 'simulated'."""
        with VulnerableAppServer("cmdi") as srv:
            payload = urllib.parse.quote("127.0.0.1; id")
            _, body = self._get(srv, f"/ping?host={payload}")
            # Simulated — not a real subprocess call
            assert "Simulated output" in body or "simulated" in body.lower()

    def test_health_endpoint(self):
        with VulnerableAppServer("cmdi") as srv:
            code, body = self._get(srv, "/health")
            assert code == 200
            assert "OK" in body
