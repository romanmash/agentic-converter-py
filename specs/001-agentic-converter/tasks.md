# Tasks: Agentic Converter

**Input**: Design documents from `/specs/001-agentic-converter/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Included — explicitly requested in spec (pytest for config, CLI, pipeline).

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize project with `uv init`, create `pyproject.toml` with dependencies (openai, pyyaml, pydantic, python-dotenv, pytest)
- [ ] T002 Create directory structure: `src/config/`, `src/agents/`, `src/graph/`, `src/llm/`, `src/prompts/`, `tests/` with `__init__.py` files
- [ ] T003 [P] Create `config.json` with defaults: `version` ("1.0.0"), `max_iterations` (5), `output_dir` ("output"), `verbose` (false), `llm.base_url`, `llm.api_key`, `llm.model`
- [ ] T004 [P] Create `.env.example` with template: `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Configuration system and LLM client that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Implement `src/config/manager.py`: `load_config()` reads `config.json`, loads `.env`, returns Pydantic `AppConfig` model
- [ ] T006 Implement config precedence: `merge_with_cli(config, cli_args)` overlays CLI arguments on loaded config
- [ ] T007 Implement `src/llm/client.py`: `LLMClient` class wrapping `openai.OpenAI(base_url, api_key)` with `chat(system_prompt, user_prompt, temperature)` method
- [ ] T008 Accept `AppConfig` in `LLMClient.__init__()` for Dependency Injection
- [ ] T009 Define `PipelineState` as Pydantic `BaseModel` in `src/graph/pipeline.py`: fields `jenkinsfile`, `workflow_yaml`, `review_feedback`, `iteration`, `status`
- [ ] T010 Create `tests/conftest.py` with shared fixtures: `mock_llm_client`, `tmp_config_dir`, `mock_env`
- [ ] T011 Write `tests/test_config.py`: test defaults, config.json overrides, env overrides, CLI precedence wins
- [ ] T012 Run `uv run pytest tests/test_config.py` — verify 100% pass

**Checkpoint**: Foundation ready — config loads, LLM client instantiates, state model validates

---

## Phase 3: User Story 1 — Single File Conversion (Priority: P1) 🎯 MVP

**Goal**: Convert one Jenkinsfile to GitHub Actions YAML via LLM

**Independent Test**: `uv run python -m src.main .data/input/1/Jenkinsfile` creates `.data/output/1/ci.yml`

### Tests for User Story 1 ⚠️

- [ ] T013 [P] [US1] Write `tests/test_cli.py`: test positional path parsing, test `--help` output, test `--version` output, test missing path error

### Implementation for User Story 1

- [ ] T014 [US1] Implement `argparse` setup in `src/main.py`: positional `path`, `-o`, `-n`, `-v`, `-V`, `-h`
- [ ] T015 [US1] Implement `--version` action reading from `load_config()`
- [ ] T016 [US1] Implement input path validation: check exists, exit code 1 if not
- [ ] T017 [P] [US1] Create `src/prompts/converter.md`: system prompt with role, Jenkins→GHA mapping rules, output-only instruction
- [ ] T018 [US1] Implement `src/agents/converter.py`: `convert(state, client)` → reads prompt, builds message, calls LLM, updates state
- [ ] T019 [US1] Wire converter into `main.py`: read Jenkinsfile → init state → call converter → validate YAML → write to output
- [ ] T020 [US1] Add YAML validation: `yaml.safe_load()` on output, warn if invalid, write anyway
- [ ] T021 [US1] Test manually: run against `.data/input/1/Jenkinsfile`, verify `.data/output/1/ci.yml`

**Checkpoint**: Single file conversion works end-to-end — MVP achieved

---

## Phase 4: User Story 2 — Iterative Quality Improvement (Priority: P1)

**Goal**: Reviewer agent evaluates YAML, feedback loop refines output

**Independent Test**: `uv run python -m src.main .data/input/1/Jenkinsfile -v` shows multi-iteration output

### Tests for User Story 2 ⚠️

- [ ] T022 [P] [US2] Write `tests/test_pipeline.py`: mock LLM returning APPROVED (1 iter), CHANGES_NEEDED→APPROVED (2 iter), max iterations exhaustion

### Implementation for User Story 2

- [ ] T023 [P] [US2] Create `src/prompts/reviewer.md`: system prompt with evaluation checklist, strict output format (STATUS/ISSUES/SUGGESTIONS)
- [ ] T024 [US2] Implement `src/agents/reviewer.py`: `review(state, client)` → reads prompt, builds message, calls LLM, parses verdict, updates state
- [ ] T025 [US2] Implement verdict parser: extract `STATUS:` line, parse ISSUES/SUGGESTIONS; unparseable → CHANGES_NEEDED
- [ ] T026 [US2] Implement `run_pipeline(jenkinsfile, client, max_iterations)` in `src/graph/pipeline.py`: loop converter→reviewer→check
- [ ] T027 [US2] Add console output: emoji progress (`🔄`, `✅`, `⚠️`), iteration counter, final status
- [ ] T028 [US2] Wire full pipeline into `main.py`, replacing single-pass call from Phase 3
- [ ] T029 [US2] Run `uv run pytest tests/test_pipeline.py` — verify mocked loop logic passes

**Checkpoint**: Agentic loop works — converter↔reviewer iterate and terminate correctly

---

## Phase 5: User Story 3 — Batch Directory Processing (Priority: P2)

**Goal**: Process multiple Jenkinsfiles from a directory with output mirroring

**Independent Test**: `uv run python -m src.main .data/input/` creates `.data/output/1/ci.yml` + `.data/output/2/ci.yml`

### Implementation for User Story 3

- [ ] T030 [US3] Implement recursive Jenkinsfile discovery: walk directory, find `Jenkinsfile`, sort alphabetically
- [ ] T031 [US3] Implement output path mirroring: compute relative path, map to `<output_dir>/<relative>/ci.yml`
- [ ] T032 [US3] Implement batch orchestration loop in `main.py`: iterate discovered files, run pipeline for each
- [ ] T033 [US3] Implement exit codes: `sys.exit(0)` all approved, `sys.exit(1)` fatal, `sys.exit(2)` partial
- [ ] T034 [US3] Test: run `uv run python -m src.main .data/input/` — verify both outputs created

**Checkpoint**: Batch mode works — directory mirroring and exit codes functional

---

## Phase 6: User Story 4 — CLI Help & Configuration (Priority: P2)

**Goal**: Polish CLI UX and verify config precedence end-to-end

### Tests for User Story 4 ⚠️

- [ ] T035 [P] [US4] Add to `tests/test_cli.py`: test all flags (`-o`, `-n`, `-v`), test defaults from config.json

### Implementation for User Story 4

- [ ] T036 [US4] Enhance `--help` output with usage examples in epilog
- [ ] T037 [US4] Run `uv run pytest` — verify all tests pass (config, cli, pipeline)

**Checkpoint**: CLI fully polished, all tests green

---

## Phase 7: User Story 5 — Documentation & Release (Priority: P3)

**Goal**: Professional documentation and release artifacts

### Implementation for User Story 5

- [ ] T038 [US5] Update `README.md`: verify Quick Start instructions work, update CLI Reference to match actual implementation, add any missing sections
- [ ] T039 [P] [US5] Update `CHANGELOG.md`: verify all implemented features are listed, update date if needed
- [ ] T040 [US5] Verify Clean Architecture: audit that `main.py` is the only I/O file, agents are pure functions
- [ ] T041 [US5] Verify no hardcoded version: search `.py` files, confirm `--version` reads config.json
- [ ] T042 [US5] Final validation: run all acceptance scenarios from spec.md

**Checkpoint**: Project complete — documentation, tests, and all acceptance criteria satisfied

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — MVP
- **US2 (Phase 4)**: Depends on US1 (extends single-pass to loop)
- **US3 (Phase 5)**: Depends on US2 (batch uses the full pipeline)
- **US4 (Phase 6)**: Can start after Foundational but best after US3
- **US5 (Phase 7)**: Depends on all stories complete

### Parallel Opportunities

- T003 + T004 (config files — different files)
- T013 (tests) alongside T017 (prompts) — different files
- T022 (test_pipeline) alongside T023 (reviewer prompt) — different files
- T035 (CLI tests) alongside T038 (README) — different files

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 + Phase 2 → Foundation ready
2. Complete Phase 3 → Single file conversion works
3. **STOP and VALIDATE**: Test against `input/1/Jenkinsfile`

### Incremental Delivery

1. Foundation → US1 (MVP!) → US2 (quality loop) → US3 (batch) → US4 (polish) → US5 (docs)
2. Each phase adds value without breaking previous phases

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Commit after each phase completion
- Stop at any checkpoint to validate independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies
