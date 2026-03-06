# AGENTS.md

Instructions for AI coding assistants working on this repository.

## Project Overview

AgenticConverter is a CLI tool that converts Jenkinsfiles to GitHub Actions YAML using a local LLM and an iterative agentic loop. See [CONTRIBUTING.md](CONTRIBUTING.md) for project principles.

## Architecture

```
src/main.py          → CLI entry point, ALL file I/O lives here
src/config/manager.py → Configuration loading (config/config.json + config/config.local.json + CLI)
src/agents/          → Converter and Reviewer agents (pure functions, no I/O)
src/graph/pipeline.py → PipelineState model + orchestration loop
src/report/generator.py → Conversion report generation (pure function)
src/llm/client.py    → OpenAI SDK wrapper (injected, not global)
src/prompts/         → System prompts as Markdown files
tests/               → pytest (must pass WITHOUT LM Studio running)
```

## Rules

1. **No hardcoded values** — all config in `config/config.json`, `config/config.local.json`, or CLI
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
| `CONTRIBUTING.md` | Project principles + contribution workflow | Update when process changes |
| `config/config.json` | App defaults (iterations + runtime settings) | Update defaults as needed |
| `config/config.local.example.json` | Optional local override template | Update examples as needed |
| `specs/001-agentic-converter/` | Feature spec, plan, tasks | Reference only |
| `docs/CASE.md` | Original customer case brief | Never modify |
| `src/prompts/*.md` | LLM system prompts | Iterate freely |

## Safety

- The tool itself makes **no direct external network calls** — it communicates only with a local OpenAI-compatible endpoint
- `config/config.local.json` is gitignored — use it for machine-specific overrides
- `.data/` is gitignored — working data only (input Jenkinsfiles + output YAML)
