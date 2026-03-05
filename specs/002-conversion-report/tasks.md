# Tasks: Conversion Report (Spec 002)

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Phase 1: Data Model Extension

- [ ] T043 Extend `PipelineState` with `history: list[IterationRecord]` field
- [ ] T044 Create `IterationRecord` Pydantic model (`iteration`, `action`, `result`)
- [ ] T045 Update `run_pipeline()` to append history records on each convert/review step
- [ ] T046 Verify existing tests still pass with extended model

## Phase 2: Report Generator

- [ ] T047 Create `src/report/__init__.py`
- [ ] T048 Implement `compute_confidence(status, iteration) → str`
- [ ] T049 Implement `generate_report(state, source_path, output_path) → str` with full template
- [ ] T050 Define static checklist as constant (11 items)

## Phase 3: Integration

- [ ] T051 Wire report generation into `main.py` after writing `ci.yml`
- [ ] T052 Write `report.md` to same output directory as `ci.yml`

## Phase 4: Testing

- [ ] T053 Write `tests/test_report.py`: confidence logic tests
- [ ] T054 Write `tests/test_report.py`: report content tests (header, checklist, history, YAML embed)
- [ ] T055 Write `tests/test_report.py`: edge cases (ERROR status, no feedback)
- [ ] T056 Update pipeline tests to verify history tracking
- [ ] T057 Run full test suite: `uv run pytest`

## Phase 5: Version & Documentation

- [ ] T058 Bump version: `config.json`, `pyproject.toml` → `1.1.0`
- [ ] T059 Update `CHANGELOG.md`: add `[1.1.0]` entry
- [ ] T060 Update `README.md`: document report feature
- [ ] T061 Commit: `feat(report): add conversion report generation (v1.1.0)`
