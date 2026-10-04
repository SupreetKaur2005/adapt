"""Callable tool the Red Team LLM invokes to execute a payload against a
sandbox target.

Targets are Docker containers in the sandbox network (see
docker/docker-compose.yml, sandbox/container_manager.py) -- `target_host`
is the container name, and the payload runs inside it via `docker exec`,
never on the host.
"""
from __future__ import annotations

import subprocess


def payload_execute(target_host: str, payload: str, timeout: float = 30.0) -> dict:
    try:
        result = subprocess.run(
            ["docker", "exec", target_host, "sh", "-c", payload],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "target_host": target_host,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except Exception as e:
        return {
            "target_host": target_host,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
        }
