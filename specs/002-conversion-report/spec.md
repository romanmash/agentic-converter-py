# Feature Specification: Conversion Report

**Feature Branch**: `002-conversion-report`
**Created**: 2026-03-05
**Status**: Draft
**Input**: "Generate a conversion report alongside each ci.yml that tells the user how reliable the output is and what may need manual fixing."

## Background

Research from `.tmp/research/` shows that even GitHub's official Actions Importer achieves only ~80% conversion target, with ~50% of real-world pipelines needing manual fixes (Slack Engineering data). Common issues requiring human attention:

| Category | Examples | Why LLM May Miss |
|---|---|---|
| **Secrets & Credentials** | Jenkins `credentials()`, `withCredentials`, vault plugins | No visibility into Jenkins credential store |
| **Custom Jenkins Plugins** | SonarQube, Artifactory, Nexus, custom `@Library` | Plugin behavior not in training data |
| **Scripted Pipeline** | `node { }`, arbitrary Groovy, `try/catch` | Turing-complete Groovy ≠ declarative YAML |
| **Self-Hosted Runners** | Jenkins agent labels → GHA runner labels | Org-specific infrastructure mapping |
| **Environment Variables** | `withEnv`, `environment {}` blocks with dynamic values | Dynamic evaluation not statically analyzable |
| **Post-Build Actions** | `emailext`, Slack notifications, Jira integration | Plugin-specific behavior |
| **Shared Libraries** | `@Library('my-lib')` | External code not visible to converter |
| **Parallel Complexity** | `parallel` with `failFast`, nested stages | Semantic nuance in GHA `needs` graph |
| **Triggers** | `pollSCM`, `upstream`, `cron` | Jenkins-specific trigger semantics |
| **Workspace / Stash** | `stash`/`unstash`, `dir()` | GHA uses artifacts, no direct equivalent |

Users need to know **how reliable** each generated file is and **what to verify manually**.

## User Scenarios & Testing *(mandatory)*

### User Story 6 — Conversion Report (Priority: P1)

As a DevOps engineer, I want a conversion report generated alongside each output YAML so that I know how many iterations were needed, whether the result was approved, and what I should manually verify.

**Why this priority**: Without this, users must blindly trust LLM output. The report makes the tool production-ready by surfacing confidence level and actionable manual checks.

**Independent Test**: Run `uv run python -m src.main .data/input/1/Jenkinsfile -v`, verify `.data/output/1/report.md` is created with proper structure.

**Acceptance Scenarios**:

1. **Given** a successful conversion, **When** the loop terminates with APPROVED, **Then** `report.md` is created alongside `ci.yml` with status ✅, iteration count, and confidence level
2. **Given** a conversion reaching max iterations, **When** the loop terminates with MAX_ITERATIONS, **Then** `report.md` shows ⚠️ status and includes the last reviewer feedback
3. **Given** any conversion, **When** `report.md` is generated, **Then** it includes a "Manual Verification Checklist" section listing potential issues to check
4. **Given** a batch run on a directory, **When** all files are processed, **Then** each output subfolder has its own `report.md`

---

### Edge Cases

- What if the conversion errors out before producing YAML? → Report shows ❌ ERROR status with error message, no checklist
- What if the reviewer never provides feedback? → Report shows the raw status without reviewer details

## Report Format *(proposed)*

Each `report.md` should follow this unified template:

```markdown
# Conversion Report

| Field | Value |
|---|---|
| **Source** | `.data/input/1/Jenkinsfile` |
| **Output** | `.data/output/1/ci.yml` |
| **Status** | ✅ APPROVED / ⚠️ MAX_ITERATIONS / ❌ ERROR |
| **Iterations** | 2 / 5 |
| **Confidence** | HIGH / MEDIUM / LOW |
| **Generated** | 2026-03-05 16:30:00 |

## Iteration History

| # | Action | Result |
|---|---|---|
| 1 | Convert | Generated initial YAML |
| 1 | Review | CHANGES_NEEDED: Missing checkout step |
| 2 | Convert | Applied fixes |
| 2 | Review | APPROVED |

## Manual Verification Checklist

> Items below are common Jenkins→GHA conversion issues that
> automated tools frequently miss. Review each relevant item.

- [ ] **Secrets & Credentials** — Verify all `credentials()` / `withCredentials` blocks are replaced with GitHub Secrets (`${{ secrets.NAME }}`)
- [ ] **Custom Plugins** — Check for Jenkins plugin steps (SonarQube, Artifactory, etc.) that may need equivalent GitHub Actions
- [ ] **Shared Libraries** — Verify `@Library` imports are replaced with equivalent actions or composite workflows
- [ ] **Self-Hosted Runners** — Confirm `runs-on` labels match your GitHub runner infrastructure
- [ ] **Environment Variables** — Check dynamic `environment {}` blocks are correctly mapped to `env:` or `${{ vars.NAME }}`
- [ ] **Post-Build Actions** — Verify notifications (email, Slack, Jira) are handled via appropriate actions
- [ ] **Triggers** — Confirm `on:` triggers match original Jenkins trigger behavior (cron, pollSCM, upstream)
- [ ] **Artifacts & Workspace** — Verify `stash`/`unstash` replaced with `actions/upload-artifact` / `actions/download-artifact`
- [ ] **Parallel Execution** — Confirm parallel stages map to concurrent GHA jobs with correct `needs` dependencies
- [ ] **YAML Validity** — Run the generated workflow through a YAML linter or `actionlint`
- [ ] **Other** — Check for any other Jenkins-specific constructs not covered above

## Reviewer Feedback (last iteration)

<raw reviewer feedback if available, otherwise "Reviewer approved without comments">

## Generated Workflow

\`\`\`yaml
<full contents of ci.yml embedded here for self-contained reference>
\`\`\`
```

## Confidence Level Logic

| Condition | Confidence |
|---|---|
| APPROVED within ≤ 2 iterations | **HIGH** |
| APPROVED within 3–4 iterations | **MEDIUM** |
| APPROVED at iteration 5 (max) | **LOW** |
| MAX_ITERATIONS (never approved) | **LOW** |
| ERROR | **N/A** |

## Requirements *(mandatory)*

### Functional Requirements

- **FR-024**: System MUST generate a `report.md` file in the same output directory as `ci.yml` for each converted Jenkinsfile
- **FR-025**: Report MUST include: source path, output path, final status, iteration count, confidence level, and timestamp
- **FR-026**: Report MUST include an iteration history table showing each convert/review action and its result
- **FR-027**: Report MUST include a "Manual Verification Checklist" based on common Jenkins→GHA conversion pitfalls (11 items including catch-all)
- **FR-028**: Confidence level MUST be computed from final status and iteration count
- **FR-029**: Report MUST include the last reviewer feedback (if any)
- **FR-030**: Report format MUST be consistent markdown across all conversions
- **FR-031**: Report MUST embed the full generated YAML at the bottom for self-contained reference

### Key Entities (extended)

- **ConversionReport**: Data model capturing all report fields — source path, output path, status, iterations, confidence, history, reviewer feedback
- **PipelineState** (extended): Must track iteration history (action + result per step) in addition to current state

## Success Criteria *(mandatory)*

- **SC-008**: Every `ci.yml` has a corresponding `report.md` in the same directory
- **SC-009**: Report accurately reflects the actual iteration count and final status
- **SC-010**: Manual checklist includes at least 8 common Jenkins→GHA issues
- **SC-011**: Confidence level is correctly computed per the defined logic
