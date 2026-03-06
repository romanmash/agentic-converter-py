# Feature Specification: File-Only Configuration Model

**Feature Branch**: `004-file-only-configuration`  
**Created**: 2026-03-06  
**Status**: Approved  
**Input**: "Simplify configuration. Remove mixed `.env` + JSON approach. Keep defaults in config and local overrides in a local file."

## User Scenarios & Testing

### User Story 1 - Predictable Configuration Sources (Priority: P1)

As a maintainer, I want configuration to come from a small, explicit set of files plus CLI flags so runtime behavior is easy to reason about and audit.

**Independent Test**: Run with no local override, then add `config/config.local.json`, then apply CLI overrides and verify precedence.

**Acceptance Scenarios**:

1. **Given** `config/config.json` exists and no local file exists, **When** the app starts, **Then** defaults come from `config/config.json`.
2. **Given** `config/config.local.json` exists, **When** the app starts, **Then** local values override defaults.
3. **Given** CLI flags are provided, **When** runtime config is resolved, **Then** CLI values override both config files.

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST use precedence: `CLI > config/config.local.json > config/config.json`.
- **FR-002**: System MUST deep-merge nested config objects.
- **FR-003**: System MUST NOT load `.env` for runtime configuration.
- **FR-004**: Repository MUST include `config/config.local.example.json` as local-override template.
- **FR-005**: `config/config.local.json` MUST be gitignored.

## Success Criteria

- **SC-001**: Config tests validate precedence and nested override behavior.
- **SC-002**: No runtime `.env` references remain in configuration loading path.
- **SC-003**: Documentation clearly describes the file-only configuration model.
