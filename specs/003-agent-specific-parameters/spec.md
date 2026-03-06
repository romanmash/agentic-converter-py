# Feature Specification: Agent-Specific LLM Parameters

**Feature Branch**: `003-agent-specific-parameters`  
**Created**: 2026-03-05  
**Status**: Draft  
**Input**: User description: "No hardcoding. Tune Converter and Reviewer differently. Converter allows creativity, Reviewer must be strict."

## Domain Roles & Philosophy *(mandatory)*
As explicitly mandated, the two agents perform fundamentally different kinds of work:

**Converter (Synthesis)**
- **Role**: Generate new YAML structure, map Jenkins concepts → GHA.
- **Goal**: Good mapping coverage without hallucinating. Allow some creativity, but not too much.

**Reviewer (Verification + Minimal Edits)**
- **Role**: Be strict, deterministic, catch mistakes.
- **Goal**: Maximize correctness and repeatability.
- **Reason**: Reviewers should not "invent" steps; they should either approve or produce the smallest correct patch. Make it boring + consistent.

*Note on Temperature*: Temperature 0.8 is quite high for code/YAML generation — it often increases subtle YAML syntax slips, wrong action choices, and extra "helpful" but incorrect steps. Therefore, dedicated sets of parameters for both nodes are required.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Separated LLM Execution Contexts (Priority: P1)

Users want to pass distinct LLM parameters to the Converter vs. the Reviewer so that generation can be slightly creative (without hallucinating) while reviewing remains rigorously deterministic.

**Why this priority**: Temperature 0.8 is too high for YAML generation, leading to syntax slips. Splitting the parameters resolves this structural flaw.

**Independent Test**: Can be fully tested by examining the API request payload sent to the mocked OpenAI client for the converter vs. the reviewer node.

**Acceptance Scenarios**:

1. **Given** a pipeline run, **When** the Converter agent calls the LLM, **Then** it uses the configured `converter` parameters (optimizing for synthesis bounds).
2. **Given** a pipeline run, **When** the Reviewer agent calls the LLM, **Then** it uses the configured `reviewer` parameters (optimizing for deterministic verification).

---

### User Story 2 - True Single Source of Configuration (Priority: P1)

Users want `config/config.json` to be the undisputed single source of truth for defaults, so they don't have to hunt for hardcoded values in the Python codebase to understand system behavior.

**Why this priority**: Hardcoded parameters violate Clean Architecture and make tuning opaque to non-developers. Overrides must be centralized and explicit.

**Independent Test**: Can be fully tested by changing `config/config.json` and verifying behavior without recompiling/modifying Python code.

**Acceptance Scenarios**:

1. **Given** a fresh checkout, **When** no `config/config.local.json` is present, **Then** the LLM clients initialize strictly with the values written in `config/config.json`.
2. **Given** `{"llm": {"converter": {"temperature": 0.6}}}` in `config/config.local.json`, **When** the system boots, **Then** it overrides the `config/config.json` value before the graph runs.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support distinct sets of parameters for the `converter` and `reviewer` agents.
- **FR-002**: System MUST support `temperature`, `top_k`, `top_p`, and `max_tokens` for each scope, establishing defaults exactly matching the specification:
  - **Converter**: `temperature: 0.35`, `max_tokens: 4096`, `top_p: 0.95`, `top_k: 40`.
  - **Reviewer**: `temperature: 0.1`, `max_tokens: 4096`, `top_p: 0.9`, `top_k: 20`.
- **FR-003**: System MUST define the default configuration entirely within `config/config.json` with NO hardcoded default fallbacks in `manager.py`. The `config/config.json` acts as the default single source of truth.
- **FR-004**: System MUST allow `config/config.local.json` to override any parameter from `config/config.json`.
- **FR-005**: System MUST NOT allow the Python agent files (`agents/*.py`) to pass hardcoded `temperature` arguments or any other parameters to the `LLMClient`. They must use the scoped parameters injected from config.

### Key Entities *(include if feature involves data)*

- **LLMParameters**: Data structure representing the 4 tunable hyperparameters.
- **AppConfig**: The master configuration state that now holds `converter` and `reviewer` nodes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 0 remaining hardcoded `temperature=...` or `top_p=...` literals in the application source code outside of `config/config.json`.
- **SC-002**: 100% of pipeline tests pass using dynamically loaded configuration.
