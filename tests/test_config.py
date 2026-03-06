"""Tests for configuration loading and precedence.

Tests cover:
- Default values when no config file exists
- config.json overrides defaults
- config.local.json overrides config.json
- CLI arguments override everything
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.config.manager import AppConfig, LLMConfig, load_config, merge_with_cli


class TestDefaults:
    """Test default configuration validation constraints."""

    def test_max_iterations_validation(self) -> None:
        with pytest.raises(ValueError):
            AppConfig(
                max_iterations=0, 
                output_dir="foo", 
                verbose=False,
                llm=LLMConfig(
                    base_url="a", api_key="b", model="c",
                    converter={"temperature": 0.6, "max_tokens": 8192, "top_p": 0.95, "top_k": 40},
                    reviewer={"temperature": 0.2, "max_tokens": 8192, "top_p": 0.95, "top_k": 40}
                )
            )
        with pytest.raises(ValueError):
            AppConfig(
                max_iterations=21,
                output_dir="foo",
                verbose=False,
                llm=LLMConfig(
                    base_url="a", api_key="b", model="c",
                    converter={"temperature": 0.6, "max_tokens": 8192, "top_p": 0.95, "top_k": 40},
                    reviewer={"temperature": 0.2, "max_tokens": 8192, "top_p": 0.95, "top_k": 40}
                )
            )


class TestConfigJsonOverrides:
    """Test that config.json overrides default values."""

    def test_load_from_config_json(self, tmp_path: Path) -> None:
        config_data = {
            "max_iterations": 3,
            "output_dir": "custom_output",
            "verbose": True,
            "llm": {
                "base_url": "http://custom:5000/v1",
                "api_key": "custom-key",
                "model": "custom-model",
                "converter": {
                    "temperature": 0.5,
                    "max_tokens": 100,
                    "top_p": 0.5,
                    "top_k": 10,
                },
                "reviewer": {
                    "temperature": 0.1,
                    "max_tokens": 100,
                    "top_p": 0.5,
                    "top_k": 10,
                },
            },
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data), encoding="utf-8")

        config = load_config(config_path=config_file)

        assert config.max_iterations == 3
        assert config.output_dir == "custom_output"
        assert config.verbose is True
        assert config.llm.base_url == "http://custom:5000/v1"

    def test_load_missing_config_raises_validation_error(self, tmp_path: Path) -> None:
        # Since we removed all hardcoded defaults, loading from nowhere raises Pydantic error
        with pytest.raises(ValueError):
            load_config(config_path=tmp_path / "nonexistent.json")

    def test_config_local_overrides_and_deep_merges(self, tmp_path: Path) -> None:
        config_data = {
            "max_iterations": 5,
            "output_dir": ".data/output",
            "verbose": False,
            "llm": {
                "base_url": "http://base:1234/v1",
                "api_key": "base-key",
                "model": "base-model",
                "converter": {
                    "temperature": 0.35,
                    "max_tokens": 4096,
                    "top_p": 0.95,
                    "top_k": 40,
                },
                "reviewer": {
                    "temperature": 0.1,
                    "max_tokens": 4096,
                    "top_p": 0.9,
                    "top_k": 20,
                },
            },
        }
        local_data = {
            "max_iterations": 7,
            "llm": {
                "model": "local-model",
                "converter": {
                    "temperature": 0.5,
                },
            },
        }
        (tmp_path / "config.json").write_text(json.dumps(config_data), encoding="utf-8")
        (tmp_path / "config.local.json").write_text(
            json.dumps(local_data), encoding="utf-8"
        )

        config = load_config(config_path=tmp_path / "config.json")

        assert config.max_iterations == 7
        assert config.output_dir == ".data/output"
        assert config.llm.model == "local-model"
        assert config.llm.converter.temperature == 0.5
        # Deep merge keeps untouched nested values from base config.json.
        assert config.llm.converter.max_tokens == 4096
        assert config.llm.reviewer.top_k == 20


class TestCLIPrecedence:
    """Test that CLI arguments override everything."""

    def test_cli_overrides_config(self, default_config: AppConfig) -> None:
        merged = merge_with_cli(
            default_config,
            {"output_dir": "cli_output", "max_iterations": 10, "verbose": True},
        )

        assert merged.output_dir == "cli_output"
        assert merged.max_iterations == 10
        assert merged.verbose is True

    def test_cli_none_values_dont_override(self, default_config: AppConfig) -> None:
        merged = merge_with_cli(
            default_config,
            {"output_dir": None, "max_iterations": None, "verbose": None},
        )

        assert merged.max_iterations == 5
        assert merged.output_dir == ".data/output"

    def test_cli_partial_override(self, default_config: AppConfig) -> None:
        merged = merge_with_cli(default_config, {"max_iterations": 8})

        assert merged.max_iterations == 8
        assert merged.output_dir == ".data/output"  # Unchanged

    def test_full_precedence_chain(self, tmp_config_dir: Path) -> None:
        """CLI > config.local.json > config.json — the full chain."""
        local_data = {"max_iterations": 9, "output_dir": "local_output"}
        (tmp_config_dir / "config.local.json").write_text(
            json.dumps(local_data), encoding="utf-8"
        )

        # config.json sets baseline, config.local.json overrides output/iterations,
        # CLI overrides max_iterations
        config = load_config(config_path=tmp_config_dir / "config.json")
        merged = merge_with_cli(config, {"max_iterations": 15})

        # CLI wins for max_iterations
        assert merged.max_iterations == 15
        # config.json wins for untouched values
        assert merged.llm.base_url == "http://localhost:1234/v1"
        # config.local.json wins for non-overridden values
        assert merged.output_dir == "local_output"
