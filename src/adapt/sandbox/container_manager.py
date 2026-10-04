"""Spins up and tears down/resets the Docker container network defined in
docker/docker-compose.yml.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adapt.sandbox.targets.vulnerable_apps.registry import VulnerableApp

_COMPOSE_FILE = Path(__file__).resolve().parents[3] / "docker" / "docker-compose.yml"


def start() -> None:
    subprocess.run(
        ["docker", "compose", "-f", str(_COMPOSE_FILE), "up", "-d", "--build"],
        check=True,
    )


def reset() -> None:
    subprocess.run(["docker", "compose", "-f", str(_COMPOSE_FILE), "down", "-v"], check=True)
    subprocess.run(
        ["docker", "compose", "-f", str(_COMPOSE_FILE), "up", "-d", "--build"],
        check=True,
    )


def resolve_app(app_id: str) -> VulnerableApp | None:
    """Resolve an app_id to its VulnerableApp descriptor from the registry."""
    from adapt.sandbox.targets.vulnerable_apps.registry import get_app

    return get_app(app_id)


def get_app(app_id: str) -> VulnerableApp | None:
    """Look up an app_id in the vulnerable apps registry."""
    from adapt.sandbox.targets.vulnerable_apps.registry import get_app

    return get_app(app_id)


def start_app(app_id: str) -> VulnerableApp:
    """Look up an app by app_id in the registry, start its container, and return the app descriptor."""
    from adapt.sandbox.targets.vulnerable_apps.registry import get_app

    app = get_app(app_id)
    if app is None:
        raise ValueError(f"Unknown vulnerable app: {app_id}")

    subprocess.run(
        ["docker", "compose", "-f", str(_COMPOSE_FILE), "up", "-d", app.app_id],
        check=True,
    )
    return app
