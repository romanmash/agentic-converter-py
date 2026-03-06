# Implementation Plan: File-Only Configuration Model

**Branch**: `004-file-only-configuration` | **Date**: 2026-03-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-file-only-configuration/spec.md`

## Summary

Consolidate runtime configuration into JSON files and CLI flags, removing `.env` runtime loading to reduce cognitive overhead and eliminate mixed-approach drift.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: pydantic, json  
**Testing**: pytest  
**Scope**: `src/config/manager.py`, config files, docs, and config tests.

## Design Decisions

1. Keep long-term defaults in `config/config.json`.
2. Allow machine-local overrides in optional `config/config.local.json`.
3. Keep final per-run control with CLI.
4. Deep-merge nested dictionaries for LLM parameter blocks.

## Validation Strategy

- Unit-test config precedence and deep merge.
- Verify docs and examples use `config/` paths only.
