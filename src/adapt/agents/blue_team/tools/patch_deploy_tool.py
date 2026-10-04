"""Tool the Blue Team LLM invokes to deploy a synthesized patch into the sandbox."""
from __future__ import annotations

import subprocess


def patch_deploy(target_host: str, patch_diff: str) -> dict:
    # Use docker exec to pipe the patch to the target host
    # We write the patch diff to stdin of the patch command
    try:
        result = subprocess.run(
            ["docker", "exec", "-i", target_host, "patch", "-p1"],
            input=patch_diff,
            capture_output=True,
            text=True,
            timeout=30.0,
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

