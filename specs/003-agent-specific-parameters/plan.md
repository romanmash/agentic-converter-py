# Implementation Plan: Agent-Specific LLM Parameters

**Branch**: `003-agent-specific-parameters` | **Date**: 2026-03-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-agent-specific-parameters/spec.md`

## Summary

Decouple the LLM hyperparameters for the Converter and Reviewer agents so each can be tuned for their specific cognitive role. As outlined in the spec, temperature 0.8 is quite high for YAML code generation and causes subtle syntax slips, wrong action choices, and extra "helpful" incorrect steps.

We will eliminate all hardcoded LLM configuration from the codebase to enforce `config.json` as the extreme single source of truth, and ensure ALL configuration parameters (except version) can be overridden by `.env` variables.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: pydantic, python-dotenv, openai
**Storage**: N/A
**Testing**: pytest
**Target Platform**: CLI Tool
**Project Type**: standalone CLI application
**Constraints**: No hardcoded python defaults for Pydantic `LLMParameters`.
**Scale/Scope**: Impacts `config.json`, `.env`, `manager.py`, `client.py`, and both agents.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Article I (Library first) - N/A (Feature integrates into core loop)
- [x] Article II (CLI inputs/outputs) - Follows config rules
- [x] Article III (Test-First) - Must prove config parser loads variables properly.
- [x] Article VII/VIII (Simplicity/Anti-abstraction) - Using Pydantic models directly, no wrapper factory overkill.

## Project Structure

### Documentation (this feature)

```text
specs/003-agent-specific-parameters/
├── plan.md              # This file
├── spec.md              # Feature specification
└── tasks.md             # Execution task list
```

### Source Code (repository root)

```text
src/
├── agents/
│   ├── converter.py      # Remove hardcoded overrides
│   └── reviewer.py       # Remove hardcoded overrides
├── config/
│   └── manager.py        # Add Pydantic nesting and parsing logic
└── llm/
    └── client.py         # Update chat signature and create() kwargs

tests/
├── conftest.py           # Update mock values
└── test_config.py        # Add unit tests for .env overrides
```

**Structure Decision**: Extending the existing domain structure. Pydantic models in `config/manager.py` handle data sanitization, `client.py` handles API submission execution.

## Implementation Details

### Rationale: Parameter Splitting
Following the "engineer-style" split:
- **Converter (Synthesis)**:
  - *Goal*: Good mapping coverage without hallucinating. Allow some creativity, but not too much.
  - *Context*: Generates new YAML structure, maps Jenkins concepts → GHA.
  - *Target Config*: Base default parameters: `temperature=0.35`, `max_tokens=4096`, `top_p=0.95`, `top_k=40`.
- **Reviewer (Verification)**:
  - *Goal*: Maximize correctness and repeatability. Make it boring + consistent.
  - *Context*: Verification + minimal edits. Should approve or produce smallest patch, not "invent" steps.
  - *Target Config*: Temperature `0.1`, `max_tokens=4096`, `top_p=0.9`, `top_k=20`.

### Data Models (`manager.py`)
```python
class LLMParameters(BaseModel):
    temperature: float
    max_tokens: int
    top_p: float
    top_k: int

class LLMConfig(BaseModel):
    base_url: str
    api_key: str
    model: str
    converter: LLMParameters
    reviewer: LLMParameters
```
*Note: We expressly DO NOT use `Field(default=...)` on the `LLMParameters` (nor `base_url`, `api_key`, `model`, etc.) to fulfill the "no hardcoding at all in manager.py" requirement. All properties will load solely from `config.json` or `.env` overrides.*

### .Env Override Expansion
Since ALL parameters (except version) must be overridable by `.env`, `load_config` will use `os.environ.get()` to override:
- `MAX_ITERATIONS`, `OUTPUT_DIR`, `VERBOSE`
- `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`
- `LLM_CONVERTER_TEMPERATURE`, `LLM_CONVERTER_MAX_TOKENS`, `LLM_CONVERTER_TOP_P`, `LLM_CONVERTER_TOP_K`
- `LLM_REVIEWER_TEMPERATURE`, `LLM_REVIEWER_MAX_TOKENS`, `LLM_REVIEWER_TOP_P`, `LLM_REVIEWER_TOP_K`

### Client Integration
Update `LLMClient.chat()` to accept `params: LLMParameters` directly, passing its fields into `self._client.chat.completions.create(**kwargs)`. `top_k` must be passed via the `extra_body` kwarg.
