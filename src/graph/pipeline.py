"""Pipeline state model and orchestration for AgenticConverter.

Contains the PipelineState Pydantic model and the main
converter↔reviewer agentic loop.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PipelineStatus(str, Enum):
    """Status of a pipeline execution."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    CHANGES_NEEDED = "changes_needed"
    MAX_ITERATIONS = "max_iterations"
    ERROR = "error"


class PipelineState(BaseModel):
    """Core state model passed through the agentic loop.

    Tracks the Jenkinsfile content, generated YAML, reviewer feedback,
    iteration count, and current status.
    """

    jenkinsfile: str
    workflow_yaml: str = ""
    review_feedback: Optional[str] = None
    iteration: int = Field(default=0, ge=0)
    status: PipelineStatus = PipelineStatus.PENDING


def run_pipeline(
    jenkinsfile: str,
    client: "LLMClient",
    max_iterations: int = 5,
    verbose: bool = False,
) -> PipelineState:
    """Run the converter↔reviewer agentic loop.

    Iteratively converts and reviews until APPROVED or max iterations.

    Args:
        jenkinsfile: Raw Jenkinsfile content.
        client: LLM client for API calls.
        max_iterations: Maximum loop iterations before stopping.
        verbose: Print progress to console.

    Returns:
        Final PipelineState with status and workflow_yaml.
    """
    from src.agents.converter import convert
    from src.agents.reviewer import review

    state = PipelineState(jenkinsfile=jenkinsfile)

    for i in range(max_iterations):
        if verbose:
            print(f"  🔄 Iteration {i + 1}/{max_iterations}: converting...")

        # Converter pass
        state = convert(state, client)

        if verbose:
            print(f"  🔍 Iteration {i + 1}/{max_iterations}: reviewing...")

        # Reviewer pass
        state = review(state, client)

        if state.status == PipelineStatus.APPROVED:
            if verbose:
                print(f"  ✅ Approved on iteration {i + 1}")
            return state

        if verbose and state.review_feedback:
            feedback_preview = state.review_feedback[:100]
            print(f"  ⚠️  Changes needed: {feedback_preview}...")

    # Max iterations reached
    state = state.model_copy(update={"status": PipelineStatus.MAX_ITERATIONS})
    if verbose:
        print(f"  ⏱️  Max iterations ({max_iterations}) reached")
    return state
