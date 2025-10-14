"""
SchemaChat: A unified Python interface for multiple LLM chat providers with structured output support.

This package provides a consistent API for interacting with various LLM providers
including OpenAI, Ollama, and OpenRouter, with built-in support for structured
output using Pydantic models.
"""

from .core.configs.ollama import OllamaConfig
from .core.configs.openai import OpenAIConfig
from .core.base_client import BaseLLMClient
from .core.base_config import BaseConfig, ProviderType
from .providers.factory import ChatProviderFactory
from .providers.ollama import ChatOllama
from .providers.openai import ChatOpenAI

__version__ = "0.1.1"
__author__ = "Will Kang"
__email__ = "willysk73@outlook.com"

__all__ = [
    # Core base classes
    "BaseLLMClient",
    "BaseConfig",
    "ProviderType",
    
    # Configuration classes
    "OllamaConfig",
    "OpenAIConfig",
    
    # Provider implementations
    "ChatOpenAI",
    "ChatOllama",
    
    # Factory
    "ChatProviderFactory",
]
