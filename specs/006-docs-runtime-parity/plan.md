# Implementation Plan: Docs and Runtime Parity

**Branch**: `006-docs-runtime-parity` | **Date**: 2026-03-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-docs-runtime-parity/spec.md`

## Summary

Bring top-level documentation into strict alignment with current implementation so release review and pitch walkthrough reflect the real system.

## Technical Context

**Language/Version**: N/A (documentation feature)  
**Validation Inputs**: `README.md`, `docs/PITCH.md`, `pyproject.toml`, runtime `--help` output  
**Scope**: repository docs only.

## Design Decisions

1. CLI reference text is taken from actual runtime output rather than hand-crafted summaries.
2. Repository structure lists major tracked assets used by reviewers and presenters.
3. Pitch technical statements use project metadata as source of truth.

## Validation Strategy

- Run `uv run python -m src.main --help` and compare with README.
- Check version/requirements claims against `pyproject.toml`.
- Verify specs section includes current feature packs.
