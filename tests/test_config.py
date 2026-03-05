"""Tests for configuration loading and precedence.

Tests cover:
- Default values when no config file exists
- config.json overrides defaults
- Environment variables override config.json
- CLI arguments override everything
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.config.manager import AppConfig, LLMConfig, load_config, merge_with_cli


class TestDefaults:
    """Test default configuration values."""

    def test_default_config_has_expected_values(self) -> None:
        config = AppConfig()
        assert config.version == "1.0.0"
        assert config.max_iterations == 5
        assert config.output_dir == "output"
        assert config.verbose is False

    def test_default_llm_config(self) -> None:
        config = AppConfig()
        assert config.llm.base_url == "http://localhost:1234/v1"
        assert config.llm.api_key == "lm-studio"
        assert config.llm.model == "qwen2.5-coder-14b-instruct"

    def test_max_iterations_validation(self) -> None:
        with pytest.raises(ValueError):
            AppConfig(max_iterations=0)
        with pytest.raises(ValueError):
            AppConfig(max_iterations=21)


class TestConfigJsonOverrides:
    """Test that config.json overrides default values."""

    def test_load_from_config_json(self, tmp_path: Path) -> None:
        config_data = {
            "version": "2.0.0",
            "max_iterations": 3,
            "output_dir": "custom_output",
            "verbose": True,
            "llm": {
                "base_url": "http://custom:5000/v1",
                "api_key": "custom-key",
                "model": "custom-model",
            },
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data), encoding="utf-8")

        config = load_config(config_path=config_file)

        assert config.version == "2.0.0"
        assert config.max_iterations == 3
        assert config.output_dir == "custom_output"
        assert config.verbose is True
        assert config.llm.base_url == "http://custom:5000/v1"

    def test_load_missing_config_uses_defaults(self, tmp_path: Path) -> None:
        config = load_config(config_path=tmp_path / "nonexistent.json")

        assert config.version == "1.0.0"
        assert config.max_iterations == 5


class TestEnvOverrides:
    """Test that environment variables override config.json."""

    def test_env_overrides_config_json(
        self, tmp_config_dir: Path, mock_env: None
    ) -> None:
        config = load_config(config_path=tmp_config_dir / "config.json")

        assert config.llm.base_url == "http://env-override:9999/v1"
        assert config.llm.api_key == "env-key"
        assert config.llm.model == "env-model"

    def test_env_does_not_affect_non_llm_settings(
        self, tmp_config_dir: Path, mock_env: None
    ) -> None:
        config = load_config(config_path=tmp_config_dir / "config.json")

        # Non-LLM settings should still come from config.json
        assert config.max_iterations == 5
        assert config.output_dir == "output"


class TestCLIPrecedence:
    """Test that CLI arguments override everything."""

    def test_cli_overrides_config(self) -> None:
        config = AppConfig(max_iterations=5, output_dir="output", verbose=False)

        merged = merge_with_cli(
            config,
            {"output_dir": "cli_output", "max_iterations": 10, "verbose": True},
        )

        assert merged.output_dir == "cli_output"
        assert merged.max_iterations == 10
        assert merged.verbose is True

    def test_cli_none_values_dont_override(self) -> None:
        config = AppConfig(max_iterations=5)

        merged = merge_with_cli(
            config,
            {"output_dir": None, "max_iterations": None, "verbose": None},
        )

        assert merged.max_iterations == 5
        assert merged.output_dir == "output"

    def test_cli_partial_override(self) -> None:
        config = AppConfig(max_iterations=5, output_dir="original")

        merged = merge_with_cli(config, {"max_iterations": 8})

        assert merged.max_iterations == 8
        assert merged.output_dir == "original"  # Unchanged

    def test_full_precedence_chain(
        self, tmp_config_dir: Path, mock_env: None
    ) -> None:
        """CLI > Env > config.json — the full chain."""
        # config.json sets max_iterations=5, env sets LLM, CLI overrides iterations
        config = load_config(config_path=tmp_config_dir / "config.json")
        merged = merge_with_cli(config, {"max_iterations": 15})

        # CLI wins for max_iterations
        assert merged.max_iterations == 15
        # Env wins for LLM settings
        assert merged.llm.base_url == "http://env-override:9999/v1"
        # config.json wins for non-overridden
        assert merged.output_dir == "output"
