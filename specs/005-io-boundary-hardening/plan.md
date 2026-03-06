# Implementation Plan: I/O Boundary Hardening

**Branch**: `005-io-boundary-hardening` | **Date**: 2026-03-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-io-boundary-hardening/spec.md`

## Summary

Align implementation with declared architecture by moving prompt-file reads and direct progress output out of domain modules and into the CLI boundary.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: standard library + existing project deps  
**Testing**: pytest  
**Scope**: `src/main.py`, `src/graph/pipeline.py`, `src/agents/*`, related tests.

## Design Decisions

1. Prompt loading remains in `main.py` as part of the I/O boundary.
2. Agents receive `system_prompt` as argument.
3. Pipeline receives optional `progress_callback` for verbose mode.
4. CLI computes final process exit code across `APPROVED`, `MAX_ITERATIONS`, and `ERROR`.

## Validation Strategy

- Run full test suite.
- Confirm CLI help and behavior remain stable.
- Validate no architecture-doc contradiction remains for I/O boundary rule.
