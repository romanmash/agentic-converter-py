# Feature Specification: Agentic Converter

**Feature Branch**: `001-agentic-converter`
**Created**: 2026-03-04
**Status**: Approved
**Input**: User description: "Build a tool that converts Jenkins pipeline definitions (Jenkinsfiles) into GitHub Actions workflow YAML using a local LLM and an iterative converter↔reviewer agentic loop."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Single File Conversion (Priority: P1)

As a DevOps engineer, I want to convert a single Jenkinsfile to a GitHub Actions workflow so that I can migrate one pipeline at a time.

**Why this priority**: Core functionality — without this, nothing else works. This is the MVP.

**Independent Test**: Run `uv run python -m src.main .data/input/1/Jenkinsfile` and verify `.data/output/1/ci.yml` is valid YAML covering all stages.

**Acceptance Scenarios**:

1. **Given** a valid Jenkinsfile at `.data/input/1/Jenkinsfile`, **When** I run the tool, **Then** `.data/output/1/ci.yml` is created with valid GitHub Actions YAML
2. **Given** LM Studio is not running, **When** I run the tool, **Then** I get a clear error message and exit code 1

---

### User Story 2 - Iterative Quality Improvement (Priority: P1)

As a DevOps engineer, I want the converter to iteratively improve its output based on automated review so that I get higher quality results without manual intervention.

**Why this priority**: The agentic loop is the core differentiator — it must work alongside US1.

**Independent Test**: Run with `-v` flag and observe multi-iteration output with reviewer feedback, terminating on APPROVED or max iterations.

**Acceptance Scenarios**:

1. **Given** a Jenkinsfile, **When** the reviewer approves on iteration 1, **Then** the loop terminates with status APPROVED
2. **Given** a Jenkinsfile, **When** the reviewer returns CHANGES_NEEDED, **Then** the converter re-runs with feedback and the iteration count increments
3. **Given** max iterations is 5, **When** the reviewer never approves, **Then** the loop stops at iteration 5 with status `max_iterations`

---

### User Story 3 - Batch Directory Processing (Priority: P2)

As a developer, I want to process an entire folder of Jenkinsfiles at once so that I can migrate multiple projects in bulk.

**Why this priority**: Important for real-world use but requires US1+US2 working first.

**Independent Test**: Run `uv run python -m src.main .data/input/` and verify both `.data/output/1/ci.yml` and `.data/output/2/ci.yml` are created.

**Acceptance Scenarios**:

1. **Given** a directory `.data/input/` with Jenkinsfiles in subdirectories, **When** I run the tool, **Then** all Jenkinsfiles are found recursively and processed alphabetically
2. **Given** input structure `.data/input/1/Jenkinsfile` and `.data/input/2/Jenkinsfile`, **When** processed, **Then** output mirrors the structure: `.data/output/1/ci.yml` and `.data/output/2/ci.yml`

---

### User Story 4 - CLI Help & Configuration (Priority: P2)

As a developer, I want a clear `--help` command and a config file so that I can understand and customize the tool without reading source code.

**Why this priority**: Essential for usability but not core conversion logic.

**Independent Test**: Run `--help` and `--version` and verify output. Modify `config.json` and verify defaults change.

**Acceptance Scenarios**:

1. **Given** the tool is installed, **When** I run `--help`, **Then** I see dual-mode usage (positional + named options), all flags, and examples
2. **Given** the tool is installed, **When** I run `--version`, **Then** I see the version from `config.json` (e.g., `1.0.0`)
3. **Given** `config.json` sets `max_iterations: 3`, **When** I run without `-n`, **Then** the loop uses 3 iterations
4. **Given** I pass `-n 10` on the CLI, **When** `config.json` says 5, **Then** CLI wins (precedence: CLI > Env > Config)

---

### User Story 5 - Documentation & Release (Priority: P3)

As a team lead, I want professional documentation so that new team members can understand and use the tool.

**Why this priority**: Polish — needed for handoff but not for core functionality.

**Independent Test**: Verify `README.md` and `CHANGELOG.md` exist and are accurate.

**Acceptance Scenarios**:

1. **Given** the project is complete, **When** I read `README.md`, **Then** I can set up and use the tool following its instructions
2. **Given** any release, **When** I check `CHANGELOG.md`, **Then** all changes are documented with version numbers

---

### Edge Cases

- What happens when the input path doesn't exist? → Exit code 1 with clear error
- What happens when LM Studio returns an empty response? → Retry once, then continue to next iteration
- What happens when the generated output is not valid YAML? → Log warning, write anyway, reviewer may catch it
- What happens when the reviewer response is unparseable? → Treat as CHANGES_NEEDED with raw output as feedback

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a file path or directory path as input
- **FR-002**: System MUST read Jenkinsfile content from disk
- **FR-003**: System MUST send Jenkinsfile to an LLM with a conversion prompt
- **FR-004**: System MUST receive GitHub Actions YAML from the LLM
- **FR-005**: On subsequent iterations, system MUST include reviewer feedback in the prompt
- **FR-006**: System MUST send generated YAML and original Jenkinsfile to an LLM with a review prompt
- **FR-007**: Reviewer MUST return structured verdict: APPROVED or CHANGES_NEEDED
- **FR-008**: When changes needed, reviewer MUST provide specific issues and suggestions
- **FR-009**: System MUST implement an iterative loop: converter → reviewer → (approve or loop)
- **FR-010**: Loop MUST terminate on reviewer approval
- **FR-011**: Loop MUST terminate on configurable max iteration count
- **FR-012**: System MUST track current iteration count and state
- **FR-013**: System MUST write final YAML to disk
- **FR-014**: Output MUST be valid YAML
- **FR-015**: System MUST report final status and iteration count
- **FR-016**: System MUST find Jenkinsfiles recursively and process alphabetically when given a directory
- **FR-017**: System MUST mirror input folder structure in output directory
- **FR-018**: System MUST map Jenkins constructs to GHA equivalents (agent, stages, parallel, post, when, env)
- **FR-019**: System MUST read defaults from `config.json`
- **FR-020**: System MUST read secrets from `.env`
- **FR-021**: System MUST enforce precedence: CLI > Env > Config File
- **FR-022**: Application version MUST be in `config.json` (no hardcoded versions)
- **FR-023**: Project MUST maintain `README.md` and `CHANGELOG.md`

### Key Entities

- **PipelineState**: Core state model passed through the agentic loop — contains `jenkinsfile`, `workflow_yaml`, `review_feedback`, `iteration`, `status`
- **AppConfig**: Merged configuration from all sources — contains `version`, `max_iterations`, `output_dir`, `verbose`, `llm` settings

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Both Jenkinsfile 1 and 2 produce valid YAML that parses without errors
- **SC-002**: Generated YAML covers all stages/steps from the original Jenkinsfile
- **SC-003**: Agentic loop converges (APPROVED) within 5 iterations for both files
- **SC-004**: Total execution time per Jenkinsfile is under 5 minutes
- **SC-005**: Codebase is under 500 lines of application code (excluding prompts)
- **SC-006**: All `pytest` tests pass without LM Studio running
- **SC-007**: Configuration precedence works correctly (CLI > Env > Config)
