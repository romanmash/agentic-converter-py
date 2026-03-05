"""Tests for the conversion report generator.

Tests cover:
- Confidence level computation
- Report content structure (header, history, checklist, YAML embed)
- Edge cases (error status, no feedback, empty YAML)
"""

from __future__ import annotations

from src.graph.pipeline import IterationRecord, PipelineState, PipelineStatus
from src.report.generator import (
    MANUAL_CHECKLIST,
    compute_confidence,
    generate_report,
)


class TestConfidenceLevel:
    """Test compute_confidence logic."""

    def test_approved_iter_1_is_high(self) -> None:
        assert compute_confidence(PipelineStatus.APPROVED, 1) == "HIGH"

    def test_approved_iter_2_is_high(self) -> None:
        assert compute_confidence(PipelineStatus.APPROVED, 2) == "HIGH"

    def test_approved_iter_3_is_medium(self) -> None:
        assert compute_confidence(PipelineStatus.APPROVED, 3) == "MEDIUM"

    def test_approved_iter_4_is_medium(self) -> None:
        assert compute_confidence(PipelineStatus.APPROVED, 4) == "MEDIUM"

    def test_approved_iter_5_is_low(self) -> None:
        assert compute_confidence(PipelineStatus.APPROVED, 5) == "LOW"

    def test_max_iterations_is_low(self) -> None:
        assert compute_confidence(PipelineStatus.MAX_ITERATIONS, 5) == "LOW"

    def test_error_is_low(self) -> None:
        assert compute_confidence(PipelineStatus.ERROR, 0) == "LOW"


class TestReportContent:
    """Test generate_report produces correct structure."""

    def _make_state(
        self,
        status: PipelineStatus = PipelineStatus.APPROVED,
        iteration: int = 1,
        yaml_content: str = "name: ci\non: push",
        feedback: str | None = None,
        history: list[IterationRecord] | None = None,
    ) -> PipelineState:
        return PipelineState(
            jenkinsfile="pipeline { agent any }",
            workflow_yaml=yaml_content,
            review_feedback=feedback,
            iteration=iteration,
            status=status,
            history=history or [],
        )

    def test_header_contains_status(self) -> None:
        state = self._make_state()
        report = generate_report(state, "input/Jenkinsfile", "output/ci.yml")
        assert "✅ APPROVED" in report

    def test_header_contains_source_and_output(self) -> None:
        state = self._make_state()
        report = generate_report(state, "input/Jenkinsfile", "output/ci.yml")
        assert "`input/Jenkinsfile`" in report
        assert "`output/ci.yml`" in report

    def test_header_contains_confidence(self) -> None:
        state = self._make_state(iteration=1)
        report = generate_report(state, "s", "o")
        assert "HIGH" in report

    def test_header_contains_iteration_count(self) -> None:
        state = self._make_state(iteration=3)
        report = generate_report(state, "s", "o", max_iterations=5)
        assert "3 / 5" in report

    def test_checklist_has_11_items(self) -> None:
        assert len(MANUAL_CHECKLIST) == 11

    def test_report_contains_all_checklist_items(self) -> None:
        state = self._make_state()
        report = generate_report(state, "s", "o")
        for item in MANUAL_CHECKLIST:
            assert item in report

    def test_report_contains_checklist_header(self) -> None:
        state = self._make_state()
        report = generate_report(state, "s", "o")
        assert "## Manual Verification Checklist" in report

    def test_iteration_history_table(self) -> None:
        history = [
            IterationRecord(iteration=1, action="convert", result="Generated YAML", comment=""),
            IterationRecord(iteration=1, action="review", result="APPROVED", comment="Looks good"),
        ]
        state = self._make_state(history=history)
        report = generate_report(state, "s", "o")
        assert "## Iteration History" in report
        assert "| 1 | Convert | Generated YAML |  |" in report
        assert "| 1 | Review | APPROVED | Looks good |" in report

    def test_embedded_yaml(self) -> None:
        yaml_content = "name: ci\non: push\njobs:\n  build:\n    runs-on: ubuntu-latest"
        state = self._make_state(yaml_content=yaml_content)
        report = generate_report(state, "s", "o")
        assert "## Generated Workflow" in report
        assert "```yaml" in report
        assert "name: ci" in report
        assert "runs-on: ubuntu-latest" in report

    def test_feedback_in_history_table(self) -> None:
        history = [
            IterationRecord(iteration=2, action="review", result="CHANGES NEEDED", comment="Missing checkout step")
        ]
        state = self._make_state(history=history)
        report = generate_report(state, "s", "o")
        assert "| 2 | Review | CHANGES NEEDED | Missing checkout step |" in report


class TestReportEdgeCases:
    """Test edge cases in report generation."""

    def test_max_iterations_status(self) -> None:
        history = [
            IterationRecord(iteration=5, action="review", result="CHANGES NEEDED", comment="Still incomplete")
        ]
        state = PipelineState(
            jenkinsfile="pipeline {}",
            workflow_yaml="name: ci",
            iteration=5,
            status=PipelineStatus.MAX_ITERATIONS,
            review_feedback="Still incomplete",
            history=history,
        )
        report = generate_report(state, "s", "o", max_iterations=5)
        assert "⚠️ MAX_ITERATIONS" in report
        assert "LOW" in report
        assert "Still incomplete" in report

    def test_empty_yaml(self) -> None:
        state = PipelineState(
            jenkinsfile="pipeline {}",
            workflow_yaml="",
            iteration=0,
            status=PipelineStatus.ERROR,
        )
        report = generate_report(state, "s", "o")
        assert "# No YAML generated" in report

    def test_empty_history(self) -> None:
        state = PipelineState(
            jenkinsfile="pipeline {}",
            workflow_yaml="name: ci",
            iteration=0,
            status=PipelineStatus.ERROR,
        )
        report = generate_report(state, "s", "o")
        assert "No iteration history recorded" in report
