"""
Factory for creating chat providers.

This module provides a factory pattern implementation for creating the appropriate
chat provider based on configuration type or provider specification.
"""

import logging
from typing import Dict, Type

from core import BaseConfig, BaseLLMClient, ProviderType

from .ollama import ChatOllama
from .openai import ChatOpenAI

# Set up logging
logger = logging.getLogger(__name__)


class ChatProviderFactory:
    """Factory for creating chat provider instances."""

    # Registry of provider classes
    _providers: Dict[ProviderType, Type[BaseLLMClient]] = {
        ProviderType.OPENAI: ChatOpenAI,
        ProviderType.OLLAMA: ChatOllama,
        ProviderType.OPENROUTER: ChatOpenAI,  # Uses OpenAI-compatible interface
    }

    @classmethod
    def create_provider(cls, config: BaseConfig) -> BaseLLMClient:
        """
        Create a chat provider instance based on configuration.

        Args:
            config: Configuration object that determines the provider type

        Returns:
            Configured chat provider instance

        Raises:
            ValueError: If the provider type is not supported
            TypeError: If the configuration type is invalid
        """
        # Validate configuration
        config.validate()

        # Get provider type from config
        provider_type = config.get_provider_type()

        # Look up provider class
        provider_class = cls._providers.get(provider_type)
        if provider_class is None:
            raise ValueError(f"Unsupported provider type: {provider_type}")

        # Create and return provider instance
        logger.debug(f"Creating {provider_class.__name__} with config: {config}")
        return provider_class(config)

    @classmethod
    def get_supported_providers(cls) -> Dict[ProviderType, Type[BaseLLMClient]]:
        """
        Get all supported provider types and their classes.

        Returns:
            Dictionary mapping provider types to provider classes
        """
        return cls._providers.copy()

    @classmethod
    def is_provider_supported(cls, provider_type: ProviderType) -> bool:
        """
        Check if a provider type is supported.

        Args:
            provider_type: Provider type to check

        Returns:
            True if the provider type is supported
        """
        return provider_type in cls._providers
