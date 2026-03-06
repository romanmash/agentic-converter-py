# Feature Specification: I/O Boundary Hardening

**Feature Branch**: `005-io-boundary-hardening`  
**Created**: 2026-03-06  
**Status**: Approved  
**Input**: "I/O should be in `main.py` only. Keep agents/pipeline deterministic and side-effect free."

## User Scenarios & Testing

### User Story 1 - Pure Domain Components (Priority: P1)

As a reviewer, I want agents and pipeline orchestration to be side-effect free so architecture claims are true and tests remain stable.

**Independent Test**: Inspect domain modules and run tests to confirm no file reads or direct console output in agents/pipeline.

**Acceptance Scenarios**:

1. **Given** converter/reviewer execution, **When** prompts are needed, **Then** prompt text is injected from `main.py` (not read inside agents).
2. **Given** pipeline execution in verbose mode, **When** progress is emitted, **Then** logging is routed through an injected callback.
3. **Given** loop outcomes include `MAX_ITERATIONS`, **When** process exits, **Then** status is non-zero unless all files are approved.

---

## Requirements

### Functional Requirements

- **FR-001**: `src/agents/*.py` MUST NOT read prompt files from disk.
- **FR-002**: `run_pipeline()` MUST accept prompt text as explicit inputs.
- **FR-003**: `run_pipeline()` MUST NOT print directly; it MUST use optional callback injection.
- **FR-004**: CLI summary MUST treat `MAX_ITERATIONS` as non-success.
- **FR-005**: Report history rendering MUST remain stable with multiline reviewer feedback.

## Success Criteria

- **SC-001**: Domain modules (`agents`, `graph`, `report`) contain no direct file I/O for prompts.
- **SC-002**: Pipeline tests pass with injected prompts.
- **SC-003**: Exit-code behavior matches documented semantics for partial/non-approved outcomes.
