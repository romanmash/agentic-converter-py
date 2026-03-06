# Tasks: File-Only Configuration Model

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Phase 1: Configuration Source Cleanup

- [x] T001 Remove `.env` runtime loading path from config manager.
- [x] T002 Ensure config files live under `config/`.
- [x] T003 Add `config/config.local.example.json`.
- [x] T004 Ensure `config/config.local.json` is gitignored.

## Phase 2: Merge and Precedence

- [x] T005 Implement deep merge for nested JSON objects.
- [x] T006 Enforce precedence: CLI > local config > default config.
- [x] T007 Validate with pytest config tests.

## Phase 3: Documentation

- [x] T008 Update README and CONTRIBUTING with file-only model.
- [x] T009 Update changelog entry to reflect simplification.
