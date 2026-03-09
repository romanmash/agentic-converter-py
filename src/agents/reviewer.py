"""Reviewer agent for AgenticConverter.

Evaluates generated GitHub Actions YAML against the original
Jenkinsfile and returns a structured verdict.
"""

from __future__ import annotations

from src.config.manager import LLMParameters
from src.graph.pipeline import PipelineState, PipelineStatus
from src.llm.client import LLMClient


def _normalize_feedback(feedback: str) -> str:
    """Normalize reviewer feedback text for downstream report rendering.

    The reviewer prompt explicitly forbids markdown fences, but models may still
    emit stray fence markers (for example a trailing ``` line). Remove those
    artifacts while preserving substantive feedback content.
    """
    cleaned_lines: list[str] = []
    for line in feedback.splitlines():
        if line.strip().startswith("```"):
            continue
        cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines).strip()

    # Defensive cleanup in case a fence token is glued to the end of text.
    while cleaned.endswith("```"):
        cleaned = cleaned[:-3].rstrip()

    return cleaned


def _parse_verdict(response: str) -> tuple[PipelineStatus, str | None]:
    """Parse the reviewer's structured response.

    Extracts STATUS line and remaining content as feedback.
    If unparseable, treats as CHANGES_NEEDED with raw output.

    Args:
        response: Raw LLM response text.

    Returns:
        Tuple of (status, feedback_text_or_none).
    """
    response = response.strip()

    # Try to find STATUS line
    for line in response.splitlines():
        line_stripped = line.strip()
        if line_stripped.upper().startswith("STATUS:"):
            status_value = line_stripped.split(":", 1)[1].strip().upper()
            if "APPROVED" in status_value and "CHANGES" not in status_value:
                return PipelineStatus.APPROVED, None
            elif "CHANGES" in status_value:
                # Extract everything after the STATUS line as feedback
                status_idx = response.index(line)
                feedback = _normalize_feedback(
                    response[status_idx + len(line) :].strip()
                )
                if feedback:
                    return PipelineStatus.CHANGES_NEEDED, feedback
                return PipelineStatus.CHANGES_NEEDED, _normalize_feedback(response)

    # Unparseable — treat as CHANGES_NEEDED with raw output
    return PipelineStatus.CHANGES_NEEDED, _normalize_feedback(response)


def review(
    state: PipelineState,
    client: LLMClient,
    llm_params: LLMParameters,
    system_prompt: str,
) -> PipelineState:
    """Review generated YAML against the original Jenkinsfile.

    Args:
        state: Current pipeline state with workflow_yaml populated.
        client: LLM client for making chat requests.
        llm_params: The reviewer-scoped LLM parameters.

    Returns:
        Updated PipelineState with status and review_feedback.
    """
    user_prompt = (
        "Review the following GitHub Actions YAML conversion.\n\n"
        f"## Original Jenkinsfile\n```groovy\n{state.jenkinsfile}\n```\n\n"
        f"## Generated GitHub Actions YAML\n```yaml\n{state.workflow_yaml}\n```"
    )

    response = client.chat(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        llm_params=llm_params,
    )
    status, feedback = _parse_verdict(response)

    return state.model_copy(
        update={
            "status": status,
            "review_feedback": feedback,
        }
    )
