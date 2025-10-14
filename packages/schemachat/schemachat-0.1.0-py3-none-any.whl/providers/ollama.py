"""
Ollama chat provider implementation.

This module provides an implementation of the ChatProviderBase for Ollama APIs.
"""

import logging
from typing import Any, Dict, Optional, Type, TypeVar

import ollama
import tiktoken
from pydantic import BaseModel

from core import BaseConfig, BaseLLMClient, OllamaConfig
from core.utils import ensure_json_format

M = TypeVar("M", bound=BaseModel)

logger = logging.getLogger(__name__)


class TokenCalculator:
    """Helper class for token calculations in Ollama providers."""

    def __init__(self, encoding_name: str = "cl100k_base"):
        """
        Initialize token calculator.

        Args:
            encoding_name: Name of the tiktoken encoding to use
        """
        try:
            self.encoder = tiktoken.get_encoding(encoding_name)
        except Exception as e:
            logger.warning(f"Failed to load tiktoken encoder {encoding_name}: {e}")
            self.encoder = None

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in the given text.

        Args:
            text: Input text

        Returns:
            Number of tokens (or rough character-based estimate if encoder fails)
        """
        if self.encoder is None:
            # Fallback: rough estimate of 4 characters per token
            return len(text) // 4

        try:
            return len(self.encoder.encode(text or ""))
        except Exception as e:
            logger.warning(f"Token counting failed: {e}")
            return len(text) // 4


class ContextManager:
    """Manages context size calculations for Ollama."""

    def __init__(self, max_context_tokens: int):
        """
        Initialize context manager.

        Args:
            max_context_tokens: Maximum context size in tokens
        """
        self.max_context_tokens = max_context_tokens
        self.token_calc = TokenCalculator()

        # Context size tiers for optimization
        self.context_tiers = [
            24 * 1024,
            32 * 1024,
            64 * 1024,
            128 * 1024,
            256 * 1024,
            512 * 1024,
        ]

    def calculate_optimal_context(
        self,
        user_message: str,
        system_message: str = "",
        expected_output: int = 1024,
        buffer: int = 256,
    ) -> int:
        """
        Calculate optimal context size for the given inputs.

        Args:
            user_message: User input message
            system_message: System prompt
            expected_output: Expected output token count
            buffer: Safety buffer for tokens

        Returns:
            Optimal context size in tokens
        """
        system_tokens = self.token_calc.count_tokens(system_message)
        user_tokens = self.token_calc.count_tokens(user_message)

        required_tokens = system_tokens + user_tokens + expected_output + buffer

        # Find the smallest tier that accommodates our needs
        for tier in self.context_tiers:
            if required_tokens <= tier <= self.max_context_tokens:
                return tier

        # Fall back to maximum if we exceed all tiers
        return min(required_tokens, self.max_context_tokens)


class ChatOllama(BaseLLMClient):
    """Ollama API implementation of the chat provider interface."""

    def __init__(self, config: BaseConfig):
        """
        Initialize the Ollama chat provider.

        Args:
            config: Configuration object (must be OllamaConfig or compatible)
        """
        super().__init__(config)
        self._client = None
        self._context_manager = None

    def _validate_config(self) -> None:
        """Validate the configuration for Ollama provider."""
        if not isinstance(self.config, OllamaConfig):
            raise TypeError(f"Expected OllamaConfig, got {type(self.config).__name__}")

        self.config.validate()

    def _get_client(self) -> ollama.Client:
        """
        Get or create the Ollama client.

        Returns:
            Ollama client instance
        """
        if self._client is None:
            self._client = ollama.Client(host=self.config.base_url)
            logger.debug(f"Created new Ollama client for {self.config.model_name}")

        return self._client

    def _get_context_manager(self) -> ContextManager:
        """
        Get or create the context manager.

        Returns:
            ContextManager instance
        """
        if self._context_manager is None:
            max_tokens = self.config.get_max_context_tokens()
            self._context_manager = ContextManager(max_tokens)

        return self._context_manager

    def _determine_context_size(
        self, user_message: str, system_message: str = ""
    ) -> int:
        """
        Determine the appropriate context size for the request.

        Args:
            user_message: User message content
            system_message: System prompt

        Returns:
            Context size in tokens
        """
        config = self.config

        # Use explicit context size if set
        if config.num_ctx is not None:
            return config.num_ctx

        # Otherwise calculate optimal size
        context_mgr = self._get_context_manager()
        return context_mgr.calculate_optimal_context(user_message, system_message)

    def invoke(self, messages: str, system: str = "") -> str:
        """
        Generate a text response from the Ollama API.

        Args:
            messages: The user message to send
            system: Optional system prompt

        Returns:
            The generated response text
        """
        client = self._get_client()
        config = self.config

        try:
            # Determine optimal context size
            context_size = self._determine_context_size(messages, system)

            # Set up generation options
            options = {
                "num_ctx": context_size,
                "num_predict": config.num_predict or 8192,
            }

            # Make API call
            response = client.chat(
                model=config.model_name,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": messages},
                ],
                options=options,
                think=False,
            )

            # Extract content from response
            content = response.get("message", {}).get("content", "")
            logger.debug(
                f"Generated {len(content)} characters with context size {context_size}"
            )

            return content

        except Exception as e:
            logger.error(f"Error invoking Ollama API: {e}")
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
            # Determine optimal context size
            context_size = self._determine_context_size(messages, system)

            # Set up generation options
            options = {
                "num_ctx": context_size,
                "num_predict": config.num_predict or 8192,
            }

            # Make API call with JSON schema format
            response = client.chat(
                model=config.model_name,
                messages=[
                    {"role": "system", "content": system},
                    {
                        "role": "system",
                        "content": f"Please output your response in JSON format according to this schema: {schema}",
                    },
                    {"role": "user", "content": messages},
                ],
                options=options,
                think=False,
            )

            # Extract raw content
            raw_content = response.get("message", {}).get("content", "{}")
            logger.debug(f"Received structured response: {len(raw_content)} characters")

            # Try to parse JSON response
            return ensure_json_format(raw_content, response_model)

        except Exception as e:
            logger.error(f"Error invoking Ollama structured API: {e}")
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

        info.update(
            {
                "max_context_kb": config.max_num_ctx,
                "max_context_tokens": config.get_max_context_tokens(),
                "num_ctx": config.num_ctx,
                "num_predict": config.num_predict,
                "api_type": "Ollama",
            }
        )

        return info
