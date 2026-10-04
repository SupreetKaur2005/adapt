"""Seeded-CVE target application registry.

Each entry in VULNERABLE_APPS describes one self-contained target that the
sandbox can build and run via container_manager / docker-compose.  A target is
identified by its ``app_id``, which doubles as the Docker container name that
payload_execute_tool uses as ``target_host``.

Public surface consumed by the rest of the sandbox:
    VULNERABLE_APPS  -- list[VulnerableApp]
    get_app(app_id)  -- VulnerableApp | None
    list_app_ids()   -- list[str]
"""

from adapt.sandbox.targets.vulnerable_apps.registry import (  # noqa: F401
    VulnerableApp,
    VULNERABLE_APPS,
    get_app,
    list_app_ids,
)
