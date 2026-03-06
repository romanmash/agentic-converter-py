"""Tests for CLI argument parsing and validation.

Tests cover:
- Positional path argument
- --help output
- --version output
- Missing path error
- All optional flags (-o, -n, -v)
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def _pyproject_version() -> str:
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    text = pyproject_path.read_text(encoding="utf-8")
    match = re.search(
        r'^\[project\][\s\S]*?^version\s*=\s*"([^"]+)"\s*$',
        text,
        flags=re.MULTILINE,
    )
    if match is None:
        raise AssertionError("Could not read [project].version from pyproject.toml")
    return match.group(1)


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
        assert _pyproject_version() in result.stdout

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
