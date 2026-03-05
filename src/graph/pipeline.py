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
