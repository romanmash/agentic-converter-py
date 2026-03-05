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


class IterationRecord(BaseModel):
    """Single step in the agentic loop history."""

    iteration: int
    action: str  # "convert" or "review"
    result: str  # "Generated YAML", "APPROVED", "CHANGES NEEDED"
    comment: str = ""  # Details or reviewer feedback


class PipelineState(BaseModel):
    """Core state model passed through the agentic loop.

    Tracks the Jenkinsfile content, generated YAML, reviewer feedback,
    iteration count, current status, and full iteration history.
    """

    jenkinsfile: str
    workflow_yaml: str = ""
    review_feedback: Optional[str] = None
    iteration: int = Field(default=0, ge=0)
    status: PipelineStatus = PipelineStatus.PENDING
    history: list[IterationRecord] = Field(default_factory=list)


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
        Final PipelineState with status, workflow_yaml, and history.
    """
    from src.agents.converter import convert
    from src.agents.reviewer import review

    state = PipelineState(jenkinsfile=jenkinsfile)

    for i in range(max_iterations):
        if verbose:
            print(f"  🔄 Iteration {i + 1}/{max_iterations}: converting...")

        # Converter pass
        state = convert(state, client)

        # Record converter step
        state = state.model_copy(
            update={
                "history": state.history
                + [
                    IterationRecord(
                        iteration=state.iteration,
                        action="convert",
                        result="Generated YAML"
                        if state.iteration == 1
                        else "Applied reviewer feedback",
                        comment="",
                    )
                ]
            }
        )

        if verbose:
            print(f"  🔍 Iteration {i + 1}/{max_iterations}: reviewing...")

        # Reviewer pass
        state = review(state, client)

        # Record reviewer step
        is_approved = state.status == PipelineStatus.APPROVED
        review_result = "APPROVED" if is_approved else "CHANGES NEEDED"
        
        # Clean up feedback for report table display
        comment = ""
        if not is_approved and state.review_feedback:
            # Replace newlines with <br> to prevent breaking markdown tables
            # while preserving the full text and some structure.
            comment = state.review_feedback.strip().replace("\n", "<br>")

        state = state.model_copy(
            update={
                "history": state.history
                + [
                    IterationRecord(
                        iteration=state.iteration,
                        action="review",
                        result=review_result,
                        comment=comment,
                    )
                ]
            }
        )

        if state.status == PipelineStatus.APPROVED:
            if verbose:
                print(f"  ✅ Approved on iteration {i + 1}")
            return state

        if verbose and state.review_feedback:
            print(f"  ⚠️  Changes needed:\n{state.review_feedback}")

    # Max iterations reached
    state = state.model_copy(update={"status": PipelineStatus.MAX_ITERATIONS})
    if verbose:
        print(f"  ⏱️  Max iterations ({max_iterations}) reached")
    return state

