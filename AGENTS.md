# AGENTS.md

Instructions for AI coding assistants working on this repository.

## Project Overview

AgenticConverter is a CLI tool that converts Jenkinsfiles to GitHub Actions YAML using a local LLM and an iterative agentic loop. See [constitution.md](constitution.md) for project principles.

## Architecture

```
src/main.py          → CLI entry point, ALL file I/O lives here
src/config/manager.py → Configuration loading (config.json + .env + CLI)
src/agents/          → Converter and Reviewer agents (pure functions, no I/O)
src/graph/pipeline.py → PipelineState model + orchestration loop
src/llm/client.py    → OpenAI SDK wrapper (injected, not global)
src/prompts/         → System prompts as Markdown files
tests/               → pytest (must pass WITHOUT LM Studio running)
```

## Rules

1. **No hardcoded values** — all config in `config.json` or `.env`
2. **I/O only in `main.py`** — agents receive and return in-memory data
3. **Dependency Injection** — pass `LLMClient` and `AppConfig` to functions
4. **Tests must be offline** — mock the LLM client, never call LM Studio
5. **Conventional Commits** — `feat:`, `fix:`, `docs:`, `test:`, `chore:`

## Testing

```bash
uv run pytest           # Run all tests (no LM Studio needed)
uv run pytest -v        # Verbose output
```

## Key Files

| File | Purpose | Modify? |
|---|---|---|
| `constitution.md` | Project principles | Read-only |
| `config.json` | App defaults (version, iterations) | Update version on release |
| `specs/001-agentic-converter/` | Feature spec, plan, tasks | Reference only |
| `docs/TASK.md` | Original customer requirements | Never modify |
| `src/prompts/*.md` | LLM system prompts | Iterate freely |

## Safety

- This tool runs **locally only** — no external network calls
- `.env` contains secrets — never commit it
- `output/` is gitignored — generated files only
