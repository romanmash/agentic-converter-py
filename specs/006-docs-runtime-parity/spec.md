# Feature Specification: Docs and Runtime Parity

**Feature Branch**: `006-docs-runtime-parity`  
**Created**: 2026-03-06  
**Status**: Approved  
**Input**: "Documentation should reflect real repo structure, real CLI behavior, and actual architecture."

## User Scenarios & Testing

### User Story 1 - Trustworthy Repository Docs (Priority: P1)

As a pitch presenter, I want repo documentation to match the shipped code so the audience can trust architecture and usage claims.

**Independent Test**: Compare README/PITCH content against live CLI output, current repository tree, and `pyproject.toml`.

**Acceptance Scenarios**:

1. **Given** CLI reference in README, **When** `--help` output is checked, **Then** command usage and option descriptions match.
2. **Given** repository structure section, **When** root and `specs/` are inspected, **Then** listed important files/folders exist.
3. **Given** tech stack claims in PITCH, **When** project metadata is checked, **Then** Python version statement matches `pyproject.toml`.

---

## Requirements

### Functional Requirements

- **FR-001**: README CLI snippet MUST align with actual argparse output.
- **FR-002**: README repository structure MUST include current key tracked files/folders.
- **FR-003**: PITCH technical stack MUST match project constraints in `pyproject.toml`.
- **FR-004**: Documentation MUST avoid stale references to removed configuration approaches.

## Success Criteria

- **SC-001**: No critical doc/code mismatches remain in README and PITCH for core architecture/config/CLI behavior.
- **SC-002**: Reviewers can verify claims directly from repository and runtime output without ambiguity.
