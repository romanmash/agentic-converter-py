"""Tests for the agentic pipeline loop.

Tests cover:
- APPROVED on first iteration (1 iter)
- CHANGES_NEEDED then APPROVED (2 iter)
- Max iterations exhaustion
- Verdict parser edge cases
"""

from __future__ import annotations

from unittest.mock import MagicMock

from src.config.manager import AppConfig
from src.agents.reviewer import _parse_verdict
from src.graph.pipeline import PipelineStatus, run_pipeline


class TestVerdictParser:
    """Test the reviewer verdict parser."""

    def test_parse_approved(self) -> None:
        status, feedback = _parse_verdict("STATUS: APPROVED")
        assert status == PipelineStatus.APPROVED
        assert feedback is None

    def test_parse_changes_needed(self) -> None:
        response = (
            "STATUS: CHANGES_NEEDED\n"
            "ISSUES:\n"
            "- Missing checkout step\n"
            "SUGGESTIONS:\n"
            "- Add actions/checkout@v4"
        )
        status, feedback = _parse_verdict(response)
        assert status == PipelineStatus.CHANGES_NEEDED
        assert "Missing checkout step" in feedback

    def test_parse_unparseable_defaults_to_changes_needed(self) -> None:
        status, feedback = _parse_verdict("Some random LLM output that doesn't follow format")
        assert status == PipelineStatus.CHANGES_NEEDED
        assert feedback is not None

    def test_parse_approved_case_insensitive(self) -> None:
        status, _ = _parse_verdict("status: approved")
        assert status == PipelineStatus.APPROVED


class TestPipelineLoop:
    """Test the converter↔reviewer agentic loop."""

    def test_approved_first_iteration(self, default_config: AppConfig) -> None:
        """Mock LLM returns valid YAML and reviewer approves immediately."""
        mock_client = MagicMock()
        # Converter returns YAML, reviewer returns APPROVED
        mock_client.chat.side_effect = [
            "name: ci\non: push\njobs:\n  build:\n    runs-on: ubuntu-latest",
            "STATUS: APPROVED",
        ]

        state = run_pipeline(
            "pipeline { agent any }",
            mock_client,
            converter_params=default_config.llm.converter,
            reviewer_params=default_config.llm.reviewer,
            max_iterations=5,
        )

        assert state.status == PipelineStatus.APPROVED
        assert state.iteration == 1
        assert "name: ci" in state.workflow_yaml

    def test_changes_then_approved(self, default_config: AppConfig) -> None:
        """Mock LLM needs one rework cycle: CHANGES_NEEDED → APPROVED."""
        mock_client = MagicMock()
        mock_client.chat.side_effect = [
            # Iter 1: converter
            "name: ci\non: push",
            # Iter 1: reviewer rejects
            "STATUS: CHANGES_NEEDED\nISSUES:\n- Missing jobs section",
            # Iter 2: converter fixes
            "name: ci\non: push\njobs:\n  build:\n    runs-on: ubuntu-latest",
            # Iter 2: reviewer approves
            "STATUS: APPROVED",
        ]

        state = run_pipeline(
            "pipeline { agent any }",
            mock_client,
            converter_params=default_config.llm.converter,
            reviewer_params=default_config.llm.reviewer,
            max_iterations=5,
        )

        assert state.status == PipelineStatus.APPROVED
        assert state.iteration == 2

    def test_max_iterations_exhaustion(self, default_config: AppConfig) -> None:
        """Mock LLM never gets approved, hits max iterations."""
        mock_client = MagicMock()
        # Always return CHANGES_NEEDED
        mock_client.chat.side_effect = [
            "name: ci",
            "STATUS: CHANGES_NEEDED\nISSUES:\n- Still wrong",
        ] * 3  # 3 iterations

        state = run_pipeline(
            "pipeline { agent any }",
            mock_client,
            converter_params=default_config.llm.converter,
            reviewer_params=default_config.llm.reviewer,
            max_iterations=3,
        )

        assert state.status == PipelineStatus.MAX_ITERATIONS
        assert state.iteration == 3

    def test_single_iteration_max(self, default_config: AppConfig) -> None:
        """With max_iterations=1, loop should run exactly once."""
        mock_client = MagicMock()
        mock_client.chat.side_effect = [
            "name: ci\non: push",
            "STATUS: CHANGES_NEEDED\nISSUES:\n- Incomplete",
        ]

        state = run_pipeline(
            "pipeline { agent any }",
            mock_client,
            converter_params=default_config.llm.converter,
            reviewer_params=default_config.llm.reviewer,
            max_iterations=1,
        )

        assert state.status == PipelineStatus.MAX_ITERATIONS
        assert state.iteration == 1

    def test_routes_distinct_params_to_converter_and_reviewer(
        self, default_config: AppConfig
    ) -> None:
        """Pipeline must pass the exact scoped params to each node."""
        mock_client = MagicMock()
        mock_client.chat.side_effect = [
            "name: ci\non: push\njobs:\n  build:\n    runs-on: ubuntu-latest",
            "STATUS: APPROVED",
        ]
        converter_params = default_config.llm.converter
        reviewer_params = default_config.llm.reviewer

        run_pipeline(
            "pipeline { agent any }",
            mock_client,
            converter_params=converter_params,
            reviewer_params=reviewer_params,
            max_iterations=1,
        )

        first_call = mock_client.chat.call_args_list[0].kwargs["llm_params"]
        second_call = mock_client.chat.call_args_list[1].kwargs["llm_params"]
        assert first_call is converter_params
        assert second_call is reviewer_params
