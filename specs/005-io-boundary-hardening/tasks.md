# Tasks: I/O Boundary Hardening

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Phase 1: Refactor Prompt Flow

- [x] T001 Remove prompt-file reads from `src/agents/converter.py`.
- [x] T002 Remove prompt-file reads from `src/agents/reviewer.py`.
- [x] T003 Inject converter/reviewer system prompts through `run_pipeline()`.

## Phase 2: Refactor Progress Emission

- [x] T004 Replace direct `print()` usage in `src/graph/pipeline.py` with callback injection.
- [x] T005 Wire callback from `src/main.py` when verbose mode is enabled.

## Phase 3: Correct Runtime Outcomes

- [x] T006 Fix final exit-code summary to treat non-approved outcomes as non-success.
- [x] T007 Keep summary output explicit for approved/max-iterations/errors.

## Phase 4: Validation

- [x] T008 Update pipeline tests for new function signature.
- [x] T009 Run full pytest suite and verify pass.
