"""
OpenAI chat provider implementation.

This module provides an implementation of the ChatProviderBase for OpenAI-compatible APIs.
"""

import logging
from typing import Any, Dict, Optional, Type, TypeVar

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from ..core import BaseConfig, BaseLLMClient, OpenAIConfig
from ..core.utils import ensure_json_format

M = TypeVar("M", bound=BaseModel)

logger = logging.getLogger(__name__)


class ChatOpenAI(BaseLLMClient):
    """OpenAI API implementation of the chat provider interface."""

    def __init__(self, config: BaseConfig):
        """
        Initialize the OpenAI chat provider.

        Args:
            config: Configuration object (must be OpenAIConfig or compatible)
        """
        super().__init__(config)
        self._client = None

    def _validate_config(self) -> None:
        """Validate the configuration for OpenAI provider."""
        if not isinstance(self.config, OpenAIConfig):
            raise TypeError(f"Expected OpenAIConfig, got {type(self.config).__name__}")

        self.config.validate()

    def _get_client(self) -> OpenAI:
        """
        Get or create the OpenAI client.

        Returns:
            OpenAI client instance
        """
        if self._client is None:
            config = self.config
            self._client = OpenAI(api_key=config.api_key, base_url=config.base_url)
            logger.debug(f"Created new OpenAI client for {config.model_name}")

        return self._client

    def invoke(self, messages: str, system: str = "") -> str:
        """
        Generate a text response from the OpenAI API.

        Args:
            messages: The user message to send
            system: Optional system prompt

        Returns:
            The generated response text
        """
        client = self._get_client()
        config = self.config

        try:
            # Set up message structure
            message_list = [
                {"role": "system", "content": system},
                {"role": "user", "content": messages},
            ]

            # Prepare generation parameters
            params = {
                "model": config.model_name,
                "messages": message_list,
                "max_tokens": config.max_tokens,
            }

            # Add optional parameters if set
            if config.temperature is not None:
                params["temperature"] = config.temperature
            if config.top_p is not None:
                params["top_p"] = config.top_p

            # Make API call
            response = client.chat.completions.create(**params)

            # Extract and return content
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error invoking OpenAI API: {e}")
            raise

    def invoke_structured(
        self, messages: str, response_model: Type[M], system: str = ""
    ) -> M:
        """
        Generate a structured response using the specified Pydantic model.

        Args:
            messages: The user message to send
            response_model: Pydantic model class for structured output
            system: Optional system prompt

        Returns:
            Instance of the response_model with generated data
        """
        client = self._get_client()
        config = self.config
        schema = response_model.model_json_schema()

        try:
            # Set up message structure
            message_list: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": system},
                {
                    "role": "system",
                    "content": f"Please output your response in JSON format according to this schema: {schema}",
                },
                {"role": "user", "content": messages},
            ]

            # Create completion with JSON response format
            response = client.chat.completions.create(
                model=config.model_name,
                messages=message_list,
                max_tokens=config.max_tokens,
            )

            # Extract and parse response
            raw_content = response.choices[0].message.content or "{}"

            # Validate against the model
            return ensure_json_format(raw_content, response_model)

        except Exception as e:
            logger.error(f"Error invoking OpenAI structured API: {e}")
            raise

    def use_fallback_model(self, new_model_name: Optional[str] = None) -> None:
        """
        Change the underlying model used by the provider.

        Args:
            new_model_name: The name of the new model to switch to
        """

        if not new_model_name:
            new_model_name = self.config.fallback_model_name
        if not new_model_name:
            raise ValueError("New model name must be provided or fallback must be set")

        logger.info(f"Changing model from {self.config.model_name} to {new_model_name}")
        self.config.model_name = new_model_name
        self._client = None

    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get detailed information about this provider.

        Returns:
            Dictionary containing provider metadata
        """
        info = super().get_provider_info()
        config = self.config

        info.update({"max_tokens": config.max_tokens, "api_type": "OpenAI"})

        return info
