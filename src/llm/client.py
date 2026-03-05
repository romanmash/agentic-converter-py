"""LLM client wrapper for AgenticConverter.

Wraps the OpenAI SDK to communicate with LM Studio's
OpenAI-compatible API. Designed for Dependency Injection.
"""

from __future__ import annotations

from openai import OpenAI

from src.config.manager import AppConfig, LLMParameters


class LLMClient:
    """Wrapper around OpenAI SDK for LM Studio communication.

    Accepts AppConfig via constructor for Dependency Injection.
    """

    def __init__(self, config: AppConfig) -> None:
        """Initialize with application config.

        Args:
            config: AppConfig containing LLM connection settings.
        """
        self._config = config
        self._client = OpenAI(
            base_url=config.llm.base_url,
            api_key=config.llm.api_key,
        )
        self._model = config.llm.model

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        llm_params: LLMParameters,
    ) -> str:
        """Send a chat completion request to the LLM.

        Args:
            system_prompt: System message defining the agent's role.
            user_prompt: User message with the task input.
            llm_params: Scoped parameters for generation (temperature, top_p, top_k, max_tokens).

        Returns:
            The assistant's response text.

        Raises:
            openai.APIConnectionError: If LM Studio is unreachable.
        """
        kwargs = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": llm_params.temperature,
            "max_tokens": llm_params.max_tokens,
            "top_p": llm_params.top_p,
        }

        if llm_params.top_k is not None:
            kwargs["extra_body"] = {"top_k": llm_params.top_k}

        response = self._client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        return content if content else ""
