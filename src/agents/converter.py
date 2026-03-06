"""Converter agent for AgenticConverter.

Reads a Jenkinsfile and produces GitHub Actions YAML
by calling the LLM with the converter system prompt.
"""

from __future__ import annotations

from src.config.manager import LLMParameters
from src.graph.pipeline import PipelineState, PipelineStatus
from src.llm.client import LLMClient

def convert(
    state: PipelineState,
    client: LLMClient,
    llm_params: LLMParameters,
    system_prompt: str,
) -> PipelineState:
    """Convert a Jenkinsfile to GitHub Actions YAML via LLM.

    If review feedback exists (iteration > 0), it is included
    in the user prompt so the LLM can address the issues.

    Args:
        state: Current pipeline state with jenkinsfile content.
        client: LLM client for making chat requests.
        llm_params: The converter-scoped LLM parameters.

    Returns:
        Updated PipelineState with workflow_yaml populated.
    """
    # Build user prompt
    if state.iteration == 0:
        user_prompt = (
            "Convert the following Jenkinsfile to a GitHub Actions workflow YAML.\n\n"
            f"```groovy\n{state.jenkinsfile}\n```"
        )
    else:
        user_prompt = (
            "The reviewer found issues with your previous output. "
            "Please fix them and output the complete corrected YAML.\n\n"
            f"## Reviewer Feedback\n{state.review_feedback}\n\n"
            f"## Original Jenkinsfile\n```groovy\n{state.jenkinsfile}\n```\n\n"
            f"## Your Previous Output\n```yaml\n{state.workflow_yaml}\n```"
        )

    # Call LLM
    yaml_output = client.chat(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        llm_params=llm_params,
    )

    # Strip markdown fences if LLM wraps output
    yaml_output = yaml_output.strip()
    if yaml_output.startswith("```yaml"):
        yaml_output = yaml_output[7:]
    if yaml_output.startswith("```"):
        yaml_output = yaml_output[3:]
    if yaml_output.endswith("```"):
        yaml_output = yaml_output[:-3]
    yaml_output = yaml_output.strip()

    return state.model_copy(
        update={
            "workflow_yaml": yaml_output,
            "iteration": state.iteration + 1,
            "status": PipelineStatus.IN_PROGRESS,
        }
    )
