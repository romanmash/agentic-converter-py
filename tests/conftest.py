"""Shared test fixtures for AgenticConverter.

Provides mocked LLM client, temporary config directories,
and environment variable mocking. Tests run without LM Studio.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.config.manager import AppConfig, LLMConfig
from src.llm.client import LLMClient


@pytest.fixture
def default_config() -> AppConfig:
    """Return a default AppConfig for testing."""
    return AppConfig()


@pytest.fixture
def mock_llm_client() -> LLMClient:
    """Return an LLMClient with a mocked OpenAI client.

    No actual API calls are made.
    """
    config = AppConfig()
    client = LLMClient(config)
    client._client = MagicMock()
    return client


@pytest.fixture
def tmp_config_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with config.json.

    Returns the path to the temp directory.
    """
    config_data = {
        "version": "1.0.0",
        "max_iterations": 5,
        "output_dir": "output",
        "verbose": False,
        "llm": {
            "base_url": "http://localhost:1234/v1",
            "api_key": "lm-studio",
            "model": "qwen2.5-coder-14b-instruct",
        },
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data), encoding="utf-8")
    return tmp_path


@pytest.fixture
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set LLM environment variables for testing precedence."""
    monkeypatch.setenv("LLM_BASE_URL", "http://env-override:9999/v1")
    monkeypatch.setenv("LLM_API_KEY", "env-key")
    monkeypatch.setenv("LLM_MODEL", "env-model")
