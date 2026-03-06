"""Configuration manager for AgenticConverter.

Loads configuration from config/config.json, config/config.local.json, and CLI
with precedence: CLI > config/config.local.json > config/config.json.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


# --- Models ---


class LLMParameters(BaseModel):
    """Specific parameters for an LLM execution scope."""

    temperature: float
    max_tokens: int
    top_p: float
    top_k: int


class LLMConfig(BaseModel):
    """LLM connection settings and scoped parameters."""

    base_url: str
    api_key: str
    model: str
    converter: LLMParameters
    reviewer: LLMParameters


class AppConfig(BaseModel):
    """Merged application configuration from all sources."""

    max_iterations: int = Field(ge=1, le=20)
    output_dir: str
    verbose: bool
    llm: LLMConfig


# --- Loaders ---


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override dictionary into base dictionary."""
    result = dict(base)
    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """Load configuration from config/config.json and optional config/config.local.json.

    1. Read config/config.json defaults
    2. Overlay optional config/config.local.json values

    Args:
        config_path: Path to config/config.json. Defaults to project root.

    Returns:
        Merged AppConfig instance.
    """
    # Determine config/config.json location
    if config_path is None:
        config_path = (
            Path(__file__).resolve().parent.parent.parent / "config" / "config.json"
        )

    # Step 1: Load config/config.json
    config_data: dict[str, Any] = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

    # Step 2: Overlay optional config/config.local.json
    local_config_path = config_path.parent / "config.local.json"
    if local_config_path.exists():
        with open(local_config_path, "r", encoding="utf-8") as f:
            local_data = json.load(f)
        if isinstance(local_data, dict):
            config_data = _deep_merge(config_data, local_data)

    return AppConfig(**config_data)


def load_project_version(pyproject_path: Optional[Path] = None) -> str:
    """Load project version from pyproject.toml [project].version."""
    if pyproject_path is None:
        pyproject_path = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"

    if not pyproject_path.exists():
        raise FileNotFoundError(f"pyproject.toml not found: {pyproject_path}")

    in_project_section = False
    version_pattern = re.compile(r'^version\s*=\s*"([^"]+)"\s*$')

    for line in pyproject_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_project_section = stripped == "[project]"
            continue
        if not in_project_section:
            continue

        match = version_pattern.match(stripped)
        if match:
            return match.group(1)

    raise ValueError("Could not find [project].version in pyproject.toml")


def merge_with_cli(config: AppConfig, cli_args: dict[str, Any]) -> AppConfig:
    """Overlay CLI arguments on a loaded config.

    Only non-None CLI values override the config.

    Args:
        config: Base configuration from load_config().
        cli_args: Dictionary from argparse namespace (vars(args)).

    Returns:
        New AppConfig with CLI overrides applied.
    """
    overrides: dict = {}

    if cli_args.get("output_dir") is not None:
        overrides["output_dir"] = cli_args["output_dir"]
    if cli_args.get("max_iterations") is not None:
        overrides["max_iterations"] = cli_args["max_iterations"]
    if cli_args.get("verbose") is not None:
        overrides["verbose"] = cli_args["verbose"]

    if overrides:
        return config.model_copy(update=overrides)
    return config
