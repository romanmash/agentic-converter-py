"""Conversion report generator for AgenticConverter.

Produces a unified markdown report alongside each ci.yml,
documenting iteration history, confidence level, and a
manual verification checklist.
"""

from __future__ import annotations

from datetime import datetime

from src.graph.pipeline import PipelineState, PipelineStatus


# --- Static Manual Verification Checklist ---

MANUAL_CHECKLIST: list[str] = [
    "**Secrets & Credentials** — Verify all `credentials()` / `withCredentials` blocks are replaced with GitHub Secrets (`${{ secrets.NAME }}`)",
    "**Custom Plugins** — Check for Jenkins plugin steps (SonarQube, Artifactory, etc.) that may need equivalent GitHub Actions",
    "**Shared Libraries** — Verify `@Library` imports are replaced with equivalent actions or composite workflows",
    "**Self-Hosted Runners** — Confirm `runs-on` labels match your GitHub runner infrastructure",
    "**Environment Variables** — Check dynamic `environment {}` blocks are correctly mapped to `env:` or `${{ vars.NAME }}`",
    "**Post-Build Actions** — Verify notifications (email, Slack, Jira) are handled via appropriate actions",
    "**Triggers** — Confirm `on:` triggers match original Jenkins trigger behavior (cron, pollSCM, upstream)",
    "**Artifacts & Workspace** — Verify `stash`/`unstash` replaced with `actions/upload-artifact` / `actions/download-artifact`",
    "**Parallel Execution** — Confirm parallel stages map to concurrent GHA jobs with correct `needs` dependencies",
    "**YAML Validity** — Run the generated workflow through a YAML linter or `actionlint`",
    "**Other** — Check for any other Jenkins-specific constructs not covered above",
]


def compute_confidence(status: PipelineStatus, iteration: int) -> str:
    """Compute confidence level from final status and iteration count.

    Args:
        status: Final pipeline status.
        iteration: Number of iterations completed.

    Returns:
        Confidence level: 'HIGH', 'MEDIUM', or 'LOW'.
    """
    if status == PipelineStatus.APPROVED and iteration <= 2:
        return "HIGH"
    elif status == PipelineStatus.APPROVED and iteration <= 4:
        return "MEDIUM"
    else:
        return "LOW"


def _status_emoji(status: PipelineStatus) -> str:
    """Map status to emoji for report display."""
    return {
        PipelineStatus.APPROVED: "✅",
        PipelineStatus.MAX_ITERATIONS: "⚠️",
        PipelineStatus.ERROR: "❌",
    }.get(status, "❓")


def _escape_table_cell(value: str) -> str:
    """Escape markdown table delimiters in cell content."""
    return value.replace("|", r"\|")


def generate_report(
    state: PipelineState,
    source_path: str,
    output_path: str,
    max_iterations: int = 5,
) -> str:
    """Generate a unified conversion report as markdown.

    Pure function — takes state and path strings, returns markdown.
    No I/O performed.

    Args:
        state: Final pipeline state with history.
        source_path: Path to the input Jenkinsfile.
        output_path: Path to the generated ci.yml.
        max_iterations: Configured max iterations.

    Returns:
        Markdown string for report.md.
    """
    confidence = compute_confidence(state.status, state.iteration)
    emoji = _status_emoji(state.status)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines: list[str] = []

    # Header
    lines.append("# Conversion Report")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    lines.append(f"| **Source** | `{source_path}` |")
    lines.append(f"| **Output** | `{output_path}` |")
    lines.append(f"| **Status** | {emoji} {state.status.value.upper()} |")
    lines.append(f"| **Iterations** | {state.iteration} / {max_iterations} |")
    lines.append(f"| **Confidence** | {confidence} |")
    lines.append(f"| **Generated** | {timestamp} |")
    lines.append("")

    # Iteration History
    lines.append("## Iteration History")
    lines.append("")
    if state.history:
        lines.append("| # | Action | Result | Comment |")
        lines.append("|---|---|---|---|")
        for record in state.history:
            action = _escape_table_cell(record.action.capitalize())
            result = _escape_table_cell(record.result)
            comment = _escape_table_cell(record.comment)
            lines.append(
                f"| {record.iteration} | {action} | {result} | {comment} |"
            )
    else:
        lines.append("*No iteration history recorded.*")
    lines.append("")

    # Manual Verification Checklist
    lines.append("## Manual Verification Checklist")
    lines.append("")
    lines.append(
        "> Items below are common Jenkins→GHA conversion issues that"
    )
    lines.append("> automated tools frequently miss. Review each relevant item.")
    lines.append("")
    for item in MANUAL_CHECKLIST:
        lines.append(f"- [ ] {item}")
    lines.append("")

    # Generated Workflow (embedded YAML)
    lines.append("## Generated Workflow")
    lines.append("")
    lines.append("```yaml")
    lines.append(state.workflow_yaml if state.workflow_yaml else "# No YAML generated")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)
