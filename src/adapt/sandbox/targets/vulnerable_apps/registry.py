"""Registry of seeded-CVE target applications for the A.D.A.P.T. sandbox.

Every VulnerableApp entry:
  - is fully self-contained (pure Python; no internet access)
  - maps to a Docker container whose *name* == app_id
    (the same string payload_execute_tool passes as target_host)
  - declares its listening port, the CVE it simulates, and the
    injection/attack surface that Red Team's tools are expected to find

The two targets shipped here cover the scenarios referenced in the project:
    vuln-web-sqli   -- SQL-injection endpoint (simulates CVE-2019-11043-style
                       parameter injection in a minimal HTTP app)
    vuln-web-cmdi   -- OS command injection endpoint (simulates a classic
                       shell-metacharacter injection vulnerability)

Neither target makes any external network call; the "vulnerable behaviour" is
modelled in-process so unit tests can exercise the registry logic without
Docker.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class VulnerableApp:
    """Descriptor for one seeded-CVE target.

    Attributes
    ----------
    app_id:
        Unique identifier AND Docker container name used by
        ``payload_execute_tool`` as ``target_host``.
    display_name:
        Human-readable label for logging / dashboard.
    cve_ref:
        CVE or vulnerability class this target simulates (informational).
    description:
        Short narrative of the vulnerability.
    listen_port:
        Port the target service listens on inside the container.
    attack_surface:
        The HTTP path / protocol endpoint Red Team targets.
    injectable_param:
        Query-string or POST field name that is vulnerable.
    docker_image:
        Container image used by docker-compose for this target.
    in_scope_by_default:
        Whether this host is in the sandbox RoE scope by default.
    known_payloads:
        Representative attack payloads (for testing / mutation seeding).
    """

    app_id: str
    display_name: str
    cve_ref: str
    description: str
    listen_port: int
    attack_surface: str
    injectable_param: str
    docker_image: str
    in_scope_by_default: bool = True
    known_payloads: tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Registered targets
# ---------------------------------------------------------------------------

VULNERABLE_APPS: list[VulnerableApp] = [
    VulnerableApp(
        app_id="vuln-web-sqli",
        display_name="SQL Injection Target (PHP-FPM style)",
        cve_ref="CVE-2019-11043",        # representative injection class
        description=(
            "Minimal HTTP service with a raw SQL query built by string "
            "concatenation from the 'user' query parameter.  Simulates a "
            "PHP-FPM style env-var injection surface for Red Team recon and "
            "payload testing."
        ),
        listen_port=8080,
        attack_surface="/login",
        injectable_param="user",
        docker_image="adapt/vuln-web-sqli:latest",
        known_payloads=(
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT password FROM users--",
        ),
    ),
    VulnerableApp(
        app_id="vuln-web-cmdi",
        display_name="OS Command Injection Target",
        cve_ref="CWE-78",               # OS Command Injection
        description=(
            "Minimal HTTP service that passes the 'host' query parameter "
            "directly to a shell ping command without sanitisation.  Simulates "
            "a classic command-injection surface (``ping -c1 <host>``)."
        ),
        listen_port=8081,
        attack_surface="/ping",
        injectable_param="host",
        docker_image="adapt/vuln-web-cmdi:latest",
        known_payloads=(
            "127.0.0.1; id",
            "127.0.0.1 && cat /etc/passwd",
            "$(whoami)",
        ),
    ),
]

# Lookup index: app_id -> VulnerableApp
_INDEX: dict[str, VulnerableApp] = {app.app_id: app for app in VULNERABLE_APPS}


def get_app(app_id: str) -> VulnerableApp | None:
    """Return the VulnerableApp descriptor for *app_id*, or ``None``."""
    return _INDEX.get(app_id)


def list_app_ids() -> list[str]:
    """Return all registered target app IDs."""
    return list(_INDEX)
