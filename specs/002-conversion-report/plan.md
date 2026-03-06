# Implementation Plan: Conversion Report

## Technical Context

**Spec**: [specs/002-conversion-report/spec.md](../../specs/002-conversion-report/spec.md)
**Constitution check**: ✅ All principles satisfied — report generation is I/O, lives in `main.py`. PipelineState extended with Pydantic. No new dependencies needed.

## Design Decisions

### 1. Report Data Collection (PipelineState extension)

Extend `PipelineState` with an iteration history list to track each step (convert/review) and its result. This is the single-source-of-truth for the report — no separate state tracking needed.

```python
class IterationRecord(BaseModel):
    iteration: int
    action: str          # "convert" | "review"
    result: str          # summary of what happened
```

Add `history: list[IterationRecord]` to `PipelineState`.

### 2. Report Generation (new module: `src/report/generator.py`)

Pure function `generate_report(state, source_path, output_path) → str` that takes final state and paths, returns rendered markdown string. No I/O — follows Clean Architecture.

### 3. Confidence Level

Simple function `compute_confidence(status, iteration) → str`:
- APPROVED & iteration ≤ 2 → HIGH
- APPROVED & iteration 3–4 → MEDIUM
- Everything else → LOW

### 4. Where Report is Written

In `main.py` (the I/O boundary), after writing `ci.yml`, compute and write `report.md` to the same directory.

### 5. Static Checklist

Hardcoded in `src/report/generator.py` as a constant — no LLM call needed. Clean, reliable, maintainable.

## Project Structure (additions)

```text
src/
├── report/
│   ├── __init__.py
│   └── generator.py     # generate_report() + compute_confidence()

tests/
├── test_report.py        # Report generation tests
```

## Version Bump

- `CHANGELOG.md`: New entry under `[1.1.0]`
- `pyproject.toml`: `1.0.0` → `1.1.0`
