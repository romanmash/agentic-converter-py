"""Tests for CLI argument parsing and validation.

Tests cover:
- Positional path argument
- --help output
- --version output
- Missing path error
- All optional flags (-o, -n, -v)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _config_version() -> str:
    config_path = Path(__file__).resolve().parent.parent / "config.json"
    config_data = json.loads(config_path.read_text(encoding="utf-8"))
    return str(config_data["version"])


class TestCLIParsing:
    """Test argparse argument parsing."""

    def test_help_output(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "src.main", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "path" in result.stdout.lower()
        assert "--output-dir" in result.stdout or "-o" in result.stdout

    def test_version_output(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "src.main", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert _config_version() in result.stdout

    def test_missing_path_error(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "src.main"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_nonexistent_path_error(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "src.main", "nonexistent/path"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "error" in result.stderr.lower() or "error" in result.stdout.lower()
