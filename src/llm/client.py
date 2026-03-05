"""LLM client wrapper for AgenticConverter.

Wraps the OpenAI SDK to communicate with LM Studio's
OpenAI-compatible API. Designed for Dependency Injection.
"""

from __future__ import annotations

from openai import OpenAI

from src.config.manager import AppConfig


class LLMClient:
    """Wrapper around OpenAI SDK for LM Studio communication.

    Accepts AppConfig via constructor for Dependency Injection.
    """

    def __init__(self, config: AppConfig) -> None:
        """Initialize with application config.

        Args:
            config: AppConfig containing LLM connection settings.
        """
        self._client = OpenAI(
            base_url=config.llm.base_url,
            api_key=config.llm.api_key,
        )
        self._model = config.llm.model

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
    ) -> str:
        """Send a chat completion request to the LLM.

        Args:
            system_prompt: System message defining the agent's role.
            user_prompt: User message with the task input.
            temperature: Sampling temperature (lower = more deterministic).

        Returns:
            The assistant's response text.

        Raises:
            openai.APIConnectionError: If LM Studio is unreachable.
        """
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        content = response.choices[0].message.content
        return content if content else ""
