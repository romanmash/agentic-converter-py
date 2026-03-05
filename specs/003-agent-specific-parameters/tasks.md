---
description: "Task list for Agent-Specific Parameters"
---

# Tasks: Agent-Specific LLM Parameters

**Input**: Design documents from `/specs/003-agent-specific-parameters/`
**Prerequisites**: plan.md (required), spec.md (required)

## Phase 1: Setup & Foundational 

**Purpose**: Update tests and configurations to prevent CI breakage when data models change

- [x] T001 Update `config.json` with nested `converter` (temp 0.35) and `reviewer` (temp 0.1) blocks using the explicit defaults (`top_k=40/20`, `top_p=0.95/0.9`, `max_tokens=4096`).
- [x] T002 Update `.env.example` with documented variables (`LLM_CONVERTER_TEMPERATURE`, etc.).
- [x] T003 Update `tests/conftest.py` `tmp_config_dir` fixture to inject the exact JSON from T001.
- [x] T004 Update `tests/conftest.py` `mock_env` fixture to mock all `.env` overrides.

---

## Phase 2: User Story 1 - Separated LLM Execution Contexts (Priority: P1) 🎯 MVP

**Goal**: Pydantic models represent the nested states, and the agents pass them correctly to the client.

### Tests for User Story 1
- [x] T005 [P] [US1] Integration test parsing `LLMParameters` via `load_config()` in `tests/test_config.py`.
- [x] T006 [P] [US1] Unit test verifying `.env` correctly overrides nested dict values inside `manager.py`.

### Implementation for User Story 1
- [x] T007 [P] [US1] Refactor `src/config/manager.py` stripping ALL `Field(default=...)` fallbacks from models. No hardcoded params at all!
- [x] T008 [P] [US1] Update `load_config` to read environment variables and map ALL config properties (except version): `MAX_ITERATIONS`, `OUTPUT_DIR`, `VERBOSE`, plus the 3 base LLM bindings and the 8 new specific node params.
- [x] T009 [US1] Refactor `src/llm/client.py` `chat()` to accept `params: LLMParameters`. Map `temperature`, `max_tokens`, `top_p`, and conditionally `extra_body={'top_k': ...}` to the OpenAI call.
- [x] T010 [US1] Remove hardcoded `temperature` from `src/agents/reviewer.py`.
- [x] T011 [US1] Update `src/graph/pipeline.py` to route `config.llm.converter` and `config.llm.reviewer` to the respective agents.

**Checkpoint**: At this point, the system is fully dynamic, tests pass, and the user stories are fully satisfied.

---

## Phase 3: Polish & Cross-Cutting Concerns

**Purpose**: Consistency validation and release prep.

- [x] T012 Run `uv run pytest` to guarantee pipeline tests are green.
- [x] T013 Update `CHANGELOG.md` reflecting the new parameter configuration capability.
- [x] T014 Run validation on the overall config loading behavior.
