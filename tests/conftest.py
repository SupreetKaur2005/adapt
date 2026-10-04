"""Shared fixtures that mock local model calls, so the test suite runs in CI
without needing a loaded GPU.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_ollama_client() -> MagicMock:
    client = MagicMock()
    client.generate.return_value = "mocked response"
    client.chat.return_value = {"message": {"content": "mocked response"}}
    return client
