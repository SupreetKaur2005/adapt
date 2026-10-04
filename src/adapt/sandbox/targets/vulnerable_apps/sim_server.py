"""Lightweight in-process HTTP simulation of the seeded-CVE target apps.

This module exists so that:
  1. Unit tests can verify vulnerable-app behaviour without Docker.
  2. The sandbox can spin up real targets via docker-compose in production.

``VulnerableAppServer`` wraps Python's built-in ``http.server`` on a random
available port and implements the two simulated vulnerability surfaces:

  GET /login?user=<input>   -- SQL-injection surface
  GET /ping?host=<input>    -- OS command-injection surface

The server intentionally mirrors the behaviour described in the registry
(same paths, same parameter names) so Red Team tooling can be exercised
against it deterministically.

Usage in tests (context-manager form avoids port leaks):
    from adapt.sandbox.targets.vulnerable_apps.sim_server import VulnerableAppServer
    with VulnerableAppServer("sqli") as srv:
        import urllib.request
        body = urllib.request.urlopen(srv.url + "/login?user=admin").read()
"""
from __future__ import annotations

import http.server
import socket
import threading
import urllib.parse
from typing import Any


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

class _VulnHandler(http.server.BaseHTTPRequestHandler):
    """Serves two injectable endpoints for unit-test purposes."""

    # Suppress access-log noise during tests.
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        path = parsed.path

        if path == "/login":
            self._handle_sqli(params)
        elif path == "/ping":
            self._handle_cmdi(params)
        elif path == "/health":
            self._respond(200, b"OK")
        else:
            self._respond(404, b"Not Found")

    # ------------------------------------------------------------------
    # SQLi surface — /login?user=<input>
    # Simulates: SELECT * FROM users WHERE username='<input>'
    # ------------------------------------------------------------------
    _USERS: dict[str, str] = {
        "admin": "s3cr3t",
        "service": "Password123!",
    }

    def _handle_sqli(self, params: dict[str, list[str]]) -> None:
        user_input = params.get("user", [""])[0]

        # Simulate injection: OR '1'='1' style always-true bypass.
        if "'" in user_input and (
            "or" in user_input.lower()
            or "union" in user_input.lower()
            or "1=1" in user_input.replace(" ", "").lower()
        ):
            body = b"[SQLI] Authentication bypassed: admin:s3cr3t\n"
            self._respond(200, body)
            return

        # Normal path: look up user.
        username = user_input.split("'")[0].strip().rstrip("-")
        password = self._USERS.get(username)
        if password:
            body = f"[OK] Welcome {username}\n".encode()
            self._respond(200, body)
        else:
            self._respond(401, b"[FAIL] Invalid credentials\n")

    # ------------------------------------------------------------------
    # CMDi surface — /ping?host=<input>
    # Simulates: os.system(f"ping -c1 {host}")
    # Does NOT execute real shell commands — returns simulated output.
    # ------------------------------------------------------------------
    _SHELL_METACHARACTERS = frozenset(";|&`$(){}[]><\n")

    def _handle_cmdi(self, params: dict[str, list[str]]) -> None:
        host_input = params.get("host", ["127.0.0.1"])[0]

        # Detect injection: any shell metacharacter triggers simulated execution.
        if any(ch in host_input for ch in self._SHELL_METACHARACTERS):
            injected_cmd = host_input.split(";", 1)[-1].strip()
            injected_cmd = injected_cmd.lstrip("&| ").strip("()`$ ")
            simulated = _SIMULATED_CMD_OUTPUT.get(
                injected_cmd, f"sh: {injected_cmd}: simulated output\n"
            )
            body = (
                f"[CMDI] Injection detected. Simulated output:\n{simulated}\n"
            ).encode()
            self._respond(200, body)
            return

        # Normal path: clean host.
        body = (
            f"PING {host_input}: 56 data bytes\n"
            f"64 bytes from {host_input}: icmp_seq=0 ttl=64 time=0.1 ms\n"
        ).encode()
        self._respond(200, body)

    def _respond(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


# Deterministic simulated outputs for well-known injected commands.
_SIMULATED_CMD_OUTPUT: dict[str, str] = {
    "id": "uid=0(root) gid=0(root) groups=0(root)\n",
    "whoami": "root\n",
    "cat /etc/passwd": "root:x:0:0:root:/root:/bin/bash\nservice:x:1000:1000::/home/service:/bin/sh\n",
    "ls": "app.py  requirements.txt  static/\n",
    "uname -a": "Linux vuln-target 5.15.0-adapt #1 SMP x86_64 GNU/Linux\n",
}


# ---------------------------------------------------------------------------
# Server wrapper
# ---------------------------------------------------------------------------

def _find_free_port() -> int:
    """Bind to port 0 and let the OS choose a free port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class VulnerableAppServer:
    """In-process simulation of a vulnerable app target.

    Parameters
    ----------
    app_type:
        ``"sqli"`` (SQL injection) or ``"cmdi"`` (command injection).
    host:
        Bind address (default ``"127.0.0.1"``).
    port:
        Listening port.  ``0`` (default) picks a free OS port.

    Context-manager usage::

        with VulnerableAppServer("sqli") as srv:
            # srv.url == "http://127.0.0.1:<port>"
            ...
    """

    def __init__(
        self,
        app_type: str = "sqli",
        host: str = "127.0.0.1",
        port: int = 0,
    ) -> None:
        if app_type not in {"sqli", "cmdi"}:
            raise ValueError(f"Unknown app_type {app_type!r}; choose 'sqli' or 'cmdi'")
        self.app_type = app_type
        self._host = host
        self._port = port if port != 0 else _find_free_port()
        self._server: http.server.HTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def url(self) -> str:
        return f"http://{self._host}:{self._port}"

    def start(self) -> None:
        """Start the server in a background daemon thread."""
        if self._server is not None:
            return
        self._server = http.server.HTTPServer((self._host, self._port), _VulnHandler)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            daemon=True,
            name=f"VulnApp-{self.app_type}",
        )
        self._thread.start()

    def stop(self) -> None:
        """Shut the server down and wait for the thread to exit."""
        if self._server is not None:
            self._server.shutdown()
            self._server = None
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    # Context-manager support
    def __enter__(self) -> "VulnerableAppServer":
        self.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.stop()
