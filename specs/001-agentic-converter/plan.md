# Implementation Plan: Agentic Converter

**Branch**: `001-agentic-converter` | **Date**: 2026-03-05 | **Spec**: [spec.md](file:///e:/Bankdata/AgenticConverter/specs/001-agentic-converter/spec.md)
**Input**: Feature specification from `/specs/001-agentic-converter/spec.md`

## Summary

Build a CLI tool that converts Jenkinsfiles to GitHub Actions YAML using a local LLM (Qwen2.5-Coder-14B via LM Studio). The core architecture is a 2-agent iterative loop (converter→reviewer) implemented in raw Python with the OpenAI SDK. Supports single-file and batch directory processing with output mirroring.

## Technical Context

**Language/Version**: Python 3.10+
**Package Manager**: uv
**Primary Dependencies**: openai (LLM communication), pyyaml (YAML parsing), pydantic (data validation), python-dotenv (.env loading)
**Storage**: Local file system only
**Testing**: pytest (with mocked LLM client — no live inference needed)
**Target Platform**: Windows 11 with 12 GB GPU VRAM
**Project Type**: CLI tool
**Performance Goals**: < 5 minutes per Jenkinsfile conversion (including all iterations)
**Constraints**: 12 GB VRAM (Qwen2.5-Coder-14B Q4_K_M uses ~8.7 GB), no external network calls
**Scale/Scope**: 2 sample Jenkinsfiles, ~500 lines of application code

## Constitution Check

*GATE: Must pass before implementation.*

- [x] Local-only execution? — Yes, LM Studio at localhost:1234
- [x] Clean Architecture? — DI for LLM client, I/O only in main.py
- [x] No hardcoded values? — config.json + .env, version in config
- [x] Test-first where practical? — pytest for config, CLI, pipeline routing
- [x] Simplicity? — Raw Python + OpenAI SDK, no heavy framework
- [x] Versioning? — config.json version field, CHANGELOG.md

## Project Structure

### Documentation (this feature)

```text
specs/001-agentic-converter/
├── spec.md              # Feature specification
├── plan.md              # This file
└── tasks.md             # Task breakdown
```

### Source Code (repository root)

```text
src/
├── main.py                  # CLI entry point — ALL I/O lives here
├── config/
│   ├── __init__.py
│   └── manager.py           # Config loading and merging
├── agents/
│   ├── __init__.py
│   ├── converter.py         # Converter agent (Jenkinsfile → YAML)
│   └── reviewer.py          # Reviewer agent (evaluate YAML)
├── graph/
│   ├── __init__.py
│   └── pipeline.py          # PipelineState model + orchestration loop
├── llm/
│   ├── __init__.py
│   └── client.py            # OpenAI SDK wrapper for LM Studio
└── prompts/
    ├── converter.md          # Converter system prompt
    └── reviewer.md           # Reviewer system prompt

tests/
├── __init__.py
├── conftest.py              # Shared fixtures (mocked LLM, tmp dirs)
├── test_config.py
├── test_cli.py
└── test_pipeline.py

config.json                  # Default configuration (includes version)
.env.example                 # Environment variable template
pyproject.toml               # Dependencies (managed by uv)
README.md                    # User documentation
CHANGELOG.md                 # Version history
LICENSE                      # MIT License
AGENTS.md                    # AI assistant instructions
CONTRIBUTING.md              # Conventional commits, workflow
constitution.md              # Project principles
.editorconfig                # Editor formatting rules

.data/                       # Working data (gitignored)
├── input/                   # User places Jenkinsfiles here
│   ├── 1/Jenkinsfile
│   └── 2/Jenkinsfile
└── output/                  # Generated YAML (created at runtime)

docs/
└── TASK.md                  # Original customer requirements (read-only)
```

**Structure Decision**: Single-project CLI layout. `src/` for application code, `tests/` at root. Prompts stored as Markdown files alongside code for easy iteration without code changes.

## Key Design Decisions

### Agentic Framework: Raw Python + OpenAI SDK

A purpose-built 2-agent loop in ~150 lines of plain Python. LangGraph, CrewAI, and LangChain were considered but rejected as over-engineered for a 2-node graph. See `.tmp/research/FRAMEWORK_ANALYSIS.md` for full analysis.

### LLM Model: Qwen2.5-Coder-14B (Q4_K_M)

Selected for best code-generation benchmarks within the 12 GB VRAM constraint (~8.7 GB used). Qwen2.5-Coder-7B is the fallback (~5 GB).

### State Model: Pydantic BaseModel

`PipelineState` uses Pydantic for runtime validation instead of TypedDict, justifying the dependency and supporting Clean Architecture principles.

### CLI: Dual-Mode argparse

Positional argument for quick use, named options with short aliases for control. Inspired by GitHub Actions Importer patterns from `.tmp/inspiration/`.

### Configuration Precedence

CLI Arguments > Environment Variables (.env) > config.json defaults. Three layers with clean merge logic.

### Exit Codes

| Code | Meaning |
|---|---|
| `0` | All conversions completed successfully (all APPROVED) |
| `1` | Fatal error (missing input, LM Studio unreachable) |
| `2` | Partial success (some files reached max iterations) |

## Complexity Tracking

> No Constitution Check violations detected. No complexity justifications needed.
