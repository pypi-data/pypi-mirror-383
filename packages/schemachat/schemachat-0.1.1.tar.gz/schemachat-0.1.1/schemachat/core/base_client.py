"""
Abstract base class for chat providers.

This module defines the interface that all chat providers must implement,
providing a consistent API for both simple text generation and structured output.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar

from pydantic import BaseModel

M = TypeVar("M", bound=BaseModel)


class BaseLLMClient(ABC):
    """Abstract base class for all chat providers."""

    def __init__(self, config: Any):
        """
        Initialize the chat provider with configuration.

        Args:
            config: Configuration object containing provider-specific settings
        """
        self.config = config
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate the configuration for this provider."""
        pass

    @abstractmethod
    def invoke(self, messages: str, system: str = "") -> str:
        """
        Generate a text response from the chat provider.

        Args:
            messages: The user message to send
            system: Optional system prompt

        Returns:
            The generated response text
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def use_fallback_model(self, new_model_name: Optional[str] = None) -> None:
        """
        Change the underlying model used by the provider.

        Args:
            new_model_name: The name of the new model to switch to
        """
        pass

    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about this provider.

        Returns:
            Dictionary containing provider metadata
        """
        return {
            "provider_type": self.__class__.__name__,
            "model_name": getattr(self.config, "model_name", "unknown"),
            "base_url": getattr(self.config, "base_url", "unknown"),
        }

    def __repr__(self) -> str:
        info = self.get_provider_info()
        return f"{info['provider_type']}(model='{info['model_name']}')"
