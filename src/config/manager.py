"""Configuration manager for AgenticConverter.

Loads configuration from config.json, .env, and CLI arguments
with clear precedence: CLI > Environment > config.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

import os


# --- Models ---


class LLMConfig(BaseModel):
    """LLM connection settings."""

    base_url: str = "http://localhost:1234/v1"
    api_key: str = "lm-studio"
    model: str = "qwen2.5-coder-14b-instruct"


class AppConfig(BaseModel):
    """Merged application configuration from all sources."""

    version: str = "1.0.0"
    max_iterations: int = Field(default=5, ge=1, le=20)
    output_dir: str = "output"
    verbose: bool = False
    llm: LLMConfig = Field(default_factory=LLMConfig)


# --- Loaders ---


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """Load configuration from config.json and .env.

    1. Read config.json defaults
    2. Load .env into os.environ
    3. Override LLM settings from environment variables

    Args:
        config_path: Path to config.json. Defaults to project root.

    Returns:
        Merged AppConfig instance.
    """
    # Determine config.json location
    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent.parent / "config.json"

    # Step 1: Load config.json
    config_data: dict = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

    # Step 2: Load .env (does NOT override existing env vars)
    env_path = config_path.parent / ".env"
    load_dotenv(dotenv_path=env_path, override=False)

    # Step 3: Override LLM settings from env
    llm_data = config_data.get("llm", {})
    env_base_url = os.environ.get("LLM_BASE_URL")
    env_api_key = os.environ.get("LLM_API_KEY")
    env_model = os.environ.get("LLM_MODEL")

    if env_base_url:
        llm_data["base_url"] = env_base_url
    if env_api_key:
        llm_data["api_key"] = env_api_key
    if env_model:
        llm_data["model"] = env_model

    config_data["llm"] = llm_data

    return AppConfig(**config_data)


def merge_with_cli(config: AppConfig, cli_args: dict) -> AppConfig:
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
