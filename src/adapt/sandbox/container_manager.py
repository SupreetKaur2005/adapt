"""Spins up and tears down/resets the Docker container network defined in
docker/docker-compose.yml.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

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
