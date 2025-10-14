"""
SchemaChat - A unified interface for multiple LLM chat providers.

This package provides a factory pattern implementation for creating chat providers
with support for both text generation and structured output using Pydantic models.
"""

from core import (
    BaseLLMClient,
    BaseConfig,
    OllamaConfig,
    OpenAIConfig,
    ProviderType,
)
from providers import ChatProviderFactory, ChatOllama, ChatOpenAI

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "BaseLLMClient",
    "BaseConfig",
    "OllamaConfig", 
    "OpenAIConfig",
    "ProviderType",
    "ChatProviderFactory",
    "ChatOllama",
    "ChatOpenAI",
]
