# Contributing to AgenticConverter

## Project Principles

These principles govern implementation and reviews:

1. **Local-first execution**: The application targets a local OpenAI-compatible endpoint.
2. **Clean boundaries**: Keep I/O in `src/main.py`; agents and report generation stay pure.
3. **Configuration over hardcoding**: Runtime defaults come from `config/config.json`, optional machine-local overrides come from `config/config.local.json`, and CLI wins per run. Package version comes only from `pyproject.toml`.
4. **Deterministic quality checks**: Tests must pass offline with mocked LLM behavior.
5. **Practical minimalism**: Prefer the smallest correct change over speculative abstraction.

## Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
```

### Types

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `test` | Adding or fixing tests |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `chore` | Build process, tooling, dependencies |

### Examples

```
feat(cli): add --version flag reading from pyproject.toml
fix(converter): handle empty LLM response with retry
test(config): add precedence tests for local override
docs: update README with batch processing examples
chore: bump openai dependency to 1.30.0
```

## Development Workflow

1. **Read** the Project Principles section in this file
2. **Check** `specs/001-agentic-converter/tasks.md` — find the next task
3. **Implement** following the plan in `specs/001-agentic-converter/plan.md`
4. **Test** with `uv run pytest` — all tests must pass offline
5. **Commit** using conventional commit format

## Setup

```bash
uv sync                              # Install dependencies
cp config/config.local.example.json config/config.local.json  # Optional local overrides
uv run pytest                        # Verify tests pass
```

## Pull Request Checklist

- [ ] Tests pass without LM Studio (`uv run pytest`)
- [ ] No hardcoded values (`config/config.json` / `config/config.local.json` / CLI only)
- [ ] I/O only in `main.py`
- [ ] Conventional commit message
- [ ] `CHANGELOG.md` updated (if user-facing change)
