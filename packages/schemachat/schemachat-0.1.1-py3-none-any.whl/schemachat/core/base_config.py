"""
Configuration management for chat providers.

This module provides structured configuration classes with validation
and a consistent interface for all provider types.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class ProviderType(Enum):
    """Enumeration of supported chat provider types."""

    OPENAI = "openai"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"


@dataclass
class BaseConfig(ABC):
    """Base configuration class for all chat providers."""

    base_url: str
    model_name: str
    fallback_model_name: Optional[str]

    @abstractmethod
    def get_provider_type(self) -> ProviderType:
        """Return the provider type for this configuration."""
        pass

    @abstractmethod
    def validate(self) -> None:
        """Validate the configuration settings."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
