# AgenticConverter Constitution

## Core Principles

### I. Local-Only Execution
All processing MUST run entirely on the user's local machine. No external API calls, no cloud services, no data leaving the machine. The LLM is served locally via LM Studio.

### II. Clean Architecture & SOLID
Separation of Concerns: Core domain logic (agents, state machine) is decoupled from external interfaces (CLI, File System) and infrastructure (LLM API, Config Loaders). Dependencies are injected, not instantiated deep in the call stack.

### III. Configuration Over Hardcoding
All defaults MUST be externalized to `config.json`. Secrets and endpoints MUST use `.env`. No hardcoded version strings, URLs, or magic numbers in source code. Precedence: CLI > Environment > Config File.

### IV. Test-First Where Practical
Deterministic behaviors (config merging, CLI parsing, pipeline routing) MUST have pytest coverage. LLM-dependent behaviors use mocked clients. Tests MUST pass without LM Studio running.

### V. Simplicity & Minimalism
The customer explicitly requires a "practical and minimal" solution. Start simple, follow YAGNI. The codebase target is ≤500 lines of application code (excluding prompts). No frameworks heavier than what the problem demands.

### VI. Versioning
MAJOR.MINOR.PATCH format. Version defined in `config.json` only. Exposed via `--version` CLI flag. All changes documented in `CHANGELOG.md` following Keep a Changelog format.

## Technology Constraints

- **Language**: Python 3.10+
- **Package Manager**: `uv`
- **LLM Context**: The LLM must be accessible via an OpenAI-compatible endpoint (e.g., LM Studio, LightLLM).
- **CLI**: `argparse` (stdlib)
- **Testing**: `pytest`

## Quality Gates

- [ ] All config from `config.json` / `.env`? (no hardcoded values)
- [ ] `main.py` handles ALL I/O? (agents receive/return in-memory data only)
- [ ] Tests pass without network? (`uv run pytest`)
- [ ] No unnecessary abstractions? (YAGNI check)

## Governance

This constitution governs all development decisions for AgenticConverter. Amendments require documented justification and update to this file.

**Version**: 1.0.0 | **Ratified**: 2026-03-05
