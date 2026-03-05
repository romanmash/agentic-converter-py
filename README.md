# AgenticConverter

> CLI tool that converts Jenkinsfiles to GitHub Actions workflow YAML using a local LLM and an iterative agentic loop.

## Overview

AgenticConverter reads a Jenkinsfile (or a directory of Jenkinsfiles), sends it to a locally-hosted LLM, and produces GitHub Actions YAML. A **reviewer agent** evaluates the output and iterates with the converter until the result is approved or a max iteration count is reached.

```
Jenkinsfile → [Converter Agent] → YAML → [Reviewer Agent] → APPROVED ✅
                    ↑                            │
                    └── feedback (if needed) ─────┘
```

## Prerequisites

- **Python 3.10+**
- **[uv](https://docs.astral.sh/uv/)** — Python package manager
- **[LM Studio](https://lmstudio.ai/)** — local LLM server (OpenAI-compatible API)
- **Qwen2.5-Coder-14B** (Q4_K_M quantization) loaded in LM Studio (~8.7 GB VRAM)

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Configure LLM connection
cp .env.example .env
# Edit .env with your LM Studio URL (default: http://localhost:1234/v1)

# 3. Start LM Studio and load the model

# 4. Place Jenkinsfiles in .data/input/
mkdir -p .data/input/1
cp /path/to/your/Jenkinsfile .data/input/1/Jenkinsfile

# 5. Convert a single Jenkinsfile
uv run python -m src.main .data/input/1/Jenkinsfile

# 6. Or convert all Jenkinsfiles in a directory
uv run python -m src.main .data/input/
```

## CLI Reference

```
usage: main.py [-h] [-V] [-o DIR] [-n N] [-v] path

positional arguments:
  path                     Jenkinsfile or directory containing Jenkinsfiles

options:
  -h, --help               Show this help message and exit
  -V, --version            Show version from config.json
  -o, --output-dir DIR     Output directory (default: .data/output)
  -n, --max-iterations N   Max converter↔reviewer iterations (default: 5)
  -v, --verbose            Enable verbose output
```

### Examples

```bash
# Single file (positional argument)
uv run python -m src.main .data/input/1/Jenkinsfile

# Batch with verbose
uv run python -m src.main .data/input/ -n 3 -v

# Custom output directory
uv run python -m src.main .data/input/ -o results/

# Check version
uv run python -m src.main --version
```

## Configuration

Three-layer configuration with clear precedence: **CLI > Environment > config.json**

| Layer | File | Purpose |
|---|---|---|
| Defaults | `config.json` | App behavior (version, max_iterations, output_dir) |
| Secrets | `.env` | LLM connection (LLM_BASE_URL, LLM_API_KEY, LLM_MODEL) |
| Overrides | CLI args | Per-run overrides (-n, -o, -v) |

### Working Data

All runtime data lives in `.data/` (gitignored):

| Directory | Purpose |
|---|---|
| `.data/input/` | Place Jenkinsfiles here for conversion |
| `.data/output/` | Generated GitHub Actions YAML + conversion reports |

## Architecture

```
src/
├── main.py              # CLI + ALL file I/O (Clean Architecture boundary)
├── config/manager.py    # Config loading and merging
├── agents/
│   ├── converter.py     # Jenkinsfile → YAML via LLM
│   └── reviewer.py      # Evaluates YAML, returns APPROVED/CHANGES_NEEDED
├── graph/pipeline.py    # PipelineState + orchestration loop
├── report/generator.py  # Conversion report generation (confidence, checklist)
├── llm/client.py        # OpenAI SDK wrapper (Dependency Injection)
└── prompts/             # System prompts as Markdown (iterate without code changes)
```

**Key principles** (see [constitution.md](constitution.md)):
- All I/O in `main.py` — agents are pure functions
- Dependencies injected, not instantiated
- Tests run offline (mocked LLM client)

## Testing

```bash
uv run pytest           # All tests (no LM Studio needed)
uv run pytest -v        # Verbose
```

## Documentation Structure

Each piece of information lives in exactly **one place**:

| What | Where |
|---|---|
| Project principles | [constitution.md](constitution.md) |
| Requirements (user stories, FRs) | [specs/001-agentic-converter/spec.md](specs/001-agentic-converter/spec.md) |
| Technical design | [specs/001-agentic-converter/plan.md](specs/001-agentic-converter/plan.md) |
| Task breakdown | [specs/001-agentic-converter/tasks.md](specs/001-agentic-converter/tasks.md) |
| Original customer brief | [docs/TASK.md](docs/TASK.md) |

## License

[MIT](LICENSE)
