# Contributing to AgenticConverter

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
feat(cli): add --version flag reading from config.json
fix(converter): handle empty LLM response with retry
test(config): add precedence tests for env override
docs: update README with batch processing examples
chore: bump openai dependency to 1.30.0
```

## Development Workflow

1. **Read** `constitution.md` — understand the project principles
2. **Check** `specs/001-agentic-converter/tasks.md` — find the next task
3. **Implement** following the plan in `specs/001-agentic-converter/plan.md`
4. **Test** with `uv run pytest` — all tests must pass offline
5. **Commit** using conventional commit format

## Setup

```bash
uv sync                              # Install dependencies
cp .env.example .env                 # Configure LLM connection
uv run pytest                        # Verify tests pass
```

## Pull Request Checklist

- [ ] Tests pass without LM Studio (`uv run pytest`)
- [ ] No hardcoded values (config.json / .env only)
- [ ] I/O only in `main.py`
- [ ] Conventional commit message
- [ ] `CHANGELOG.md` updated (if user-facing change)
