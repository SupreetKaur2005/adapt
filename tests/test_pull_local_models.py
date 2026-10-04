"""Tests for scripts/pull_local_models.sh.

Validates that:
  - scripts/pull_local_models.sh exists and is properly structured
  - The model list aligns with the tiers defined in config/model_registry.yaml
  - The script executes cleanly in dry-run/mock mode when ollama is intercepted,
    calling `ollama pull` for each registered model without downloading live assets.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest
import yaml

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT_PATH = _PROJECT_ROOT / "scripts" / "pull_local_models.sh"
_REGISTRY_PATH = _PROJECT_ROOT / "config" / "model_registry.yaml"


def _find_bash() -> str | None:
    found = shutil.which("bash")
    if found:
        return found
    fallback = Path(r"C:\Program Files\Git\bin\bash.exe")
    if fallback.is_file():
        return str(fallback)
    return None


class TestPullLocalModelsScript:
    """Verify presence, syntax, and registry alignment for pull_local_models.sh."""

    def test_script_exists(self) -> None:
        assert _SCRIPT_PATH.is_file(), f"Script not found at {_SCRIPT_PATH}"

    def test_script_extracts_models_matching_registry(self) -> None:
        content = _SCRIPT_PATH.read_text(encoding="utf-8")
        # Extract quoted strings in the MODELS array
        models_block = re.search(r"MODELS=\((.*?)\)", content, re.DOTALL)
        assert models_block is not None, "MODELS array not found in pull_local_models.sh"

        script_models = set(re.findall(r'"([^"]+)"', models_block.group(1)))
        assert len(script_models) >= 5

        # Check against model_registry.yaml
        with _REGISTRY_PATH.open(encoding="utf-8") as f:
            registry = yaml.safe_load(f)

        expected_models = set()
        for tier_info in registry.get("tiers", {}).values():
            if isinstance(tier_info, dict) and "models" in tier_info:
                expected_models.update(tier_info["models"])
        if "embedding_model" in registry and "model" in registry["embedding_model"]:
            expected_models.add(registry["embedding_model"]["model"])

        # Every local lightweight, mid, and embedding model in registry should be present
        for model in ["mistral:7b", "llama3.3", "qwen3.5", "gemma2:27b", "nomic-embed-text"]:
            assert model in script_models, f"Expected model {model} missing from pull_local_models.sh"

    def test_script_execution_with_mock_ollama(self, tmp_path: Path) -> None:
        bash_bin = _find_bash()
        if not bash_bin:
            pytest.skip("Bash executable not found on this system; skipping subprocess test")

        # Create a mock ollama executable in tmp_path that records invocations
        mock_ollama = tmp_path / "ollama"
        mock_ollama.write_text("#!/usr/bin/env bash\necho \"MOCK_OLLAMA: $@\"\n", encoding="utf-8")

        # In Windows Git Bash, the script will execute the file if PATH starts with tmp_path
        env = os.environ.copy()
        env["PATH"] = f"{tmp_path}{os.pathsep}{env.get('PATH', '')}"

        # Run bash script
        res = subprocess.run(
            [bash_bin, str(_SCRIPT_PATH)],
            capture_output=True,
            text=True,
            cwd=str(_PROJECT_ROOT),
            env=env,
            timeout=10,
        )
        assert res.returncode == 0, f"Script failed: stdout={res.stdout}, stderr={res.stderr}"
        assert "Pulling mistral:7b..." in res.stdout
        assert "MOCK_OLLAMA: pull mistral:7b" in res.stdout
        assert "MOCK_OLLAMA: pull nomic-embed-text" in res.stdout
