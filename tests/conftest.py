"""Shared test fixtures for AgenticConverter.

Provides mocked LLM client, temporary config directories,
and local config fixtures. Tests run without LM Studio.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from src.config.manager import AppConfig
from src.llm.client import LLMClient

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_PATH = _REPO_ROOT / "config" / "config.json"


def _load_repo_config_data() -> dict[str, Any]:
    """Load baseline defaults from the repository config/config.json."""
    return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def default_config() -> AppConfig:
    return AppConfig(**_load_repo_config_data())


@pytest.fixture
def mock_llm_client(default_config: AppConfig) -> LLMClient:
    """Return an LLMClient with a mocked OpenAI client.

    No actual API calls are made.
    """
    client = LLMClient(default_config)
    client._client = MagicMock()
    return client


@pytest.fixture
def tmp_config_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with config.json.

    Returns the path to the temp directory.
    """
    config_data = _load_repo_config_data()
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data), encoding="utf-8")
    return tmp_path
