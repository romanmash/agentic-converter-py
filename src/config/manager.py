"""Configuration manager for AgenticConverter.

Loads configuration from config.json, .env, and CLI arguments
with clear precedence: CLI > Environment > config.json.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
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

    version: str
    max_iterations: int = Field(ge=1, le=20)
    output_dir: str
    verbose: bool
    llm: LLMConfig


# --- Loaders ---


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """Load configuration from config.json and .env.

    1. Read config.json defaults
    2. Load .env into os.environ
    3. Override global + LLM settings from environment variables

    Args:
        config_path: Path to config.json. Defaults to project root.

    Returns:
        Merged AppConfig instance.
    """
    # Determine config.json location
    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent.parent / "config.json"

    # Step 1: Load config.json
    config_data: dict[str, Any] = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

    # Step 2: Load .env (does NOT override existing env vars)
    env_path = config_path.parent / ".env"
    load_dotenv(dotenv_path=env_path, override=False)

    # Step 3: Override Global + LLM settings from env
    if "MAX_ITERATIONS" in os.environ:
        config_data["max_iterations"] = int(os.environ["MAX_ITERATIONS"])
    if "OUTPUT_DIR" in os.environ:
        config_data["output_dir"] = os.environ["OUTPUT_DIR"]
    if "VERBOSE" in os.environ:
        config_data["verbose"] = os.environ["VERBOSE"].lower() in ("true", "1", "yes")

    llm_data_raw = config_data.get("llm", {})
    llm_data = dict(llm_data_raw) if isinstance(llm_data_raw, dict) else {}
    
    # Base LLM Overrides
    if "LLM_BASE_URL" in os.environ:
        llm_data["base_url"] = os.environ["LLM_BASE_URL"]
    if "LLM_API_KEY" in os.environ:
        llm_data["api_key"] = os.environ["LLM_API_KEY"]
    if "LLM_MODEL" in os.environ:
        llm_data["model"] = os.environ["LLM_MODEL"]
        
    converter_raw = llm_data.get("converter", {})
    converter_data = dict(converter_raw) if isinstance(converter_raw, dict) else {}
    
    reviewer_raw = llm_data.get("reviewer", {})
    reviewer_data = dict(reviewer_raw) if isinstance(reviewer_raw, dict) else {}

    # Converter LLM Overrides
    if "LLM_CONVERTER_TEMPERATURE" in os.environ:
        converter_data["temperature"] = float(os.environ["LLM_CONVERTER_TEMPERATURE"])
    if "LLM_CONVERTER_MAX_TOKENS" in os.environ:
        converter_data["max_tokens"] = int(os.environ["LLM_CONVERTER_MAX_TOKENS"])
    if "LLM_CONVERTER_TOP_P" in os.environ:
        converter_data["top_p"] = float(os.environ["LLM_CONVERTER_TOP_P"])
    if "LLM_CONVERTER_TOP_K" in os.environ:
        converter_data["top_k"] = int(os.environ["LLM_CONVERTER_TOP_K"])

    # Reviewer LLM Overrides
    if "LLM_REVIEWER_TEMPERATURE" in os.environ:
        reviewer_data["temperature"] = float(os.environ["LLM_REVIEWER_TEMPERATURE"])
    if "LLM_REVIEWER_MAX_TOKENS" in os.environ:
        reviewer_data["max_tokens"] = int(os.environ["LLM_REVIEWER_MAX_TOKENS"])
    if "LLM_REVIEWER_TOP_P" in os.environ:
        reviewer_data["top_p"] = float(os.environ["LLM_REVIEWER_TOP_P"])
    if "LLM_REVIEWER_TOP_K" in os.environ:
        reviewer_data["top_k"] = int(os.environ["LLM_REVIEWER_TOP_K"])

    llm_data["converter"] = converter_data
    llm_data["reviewer"] = reviewer_data
    config_data["llm"] = llm_data

    return AppConfig(**config_data)


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
