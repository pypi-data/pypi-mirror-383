from dataclasses import dataclass
from typing import Optional

from ..base_config import BaseConfig, ProviderType


@dataclass
class OpenAIConfig(BaseConfig):
    """Configuration for OpenAI-compatible providers."""

    api_key: str
    max_tokens: int = 8192
    temperature: Optional[float] = None
    top_p: Optional[float] = None

    def get_provider_type(self) -> ProviderType:
        return ProviderType.OPENAI

    def validate(self) -> None:
        if not self.api_key:
            raise ValueError("API key is required for OpenAI provider")
        if not self.base_url:
            raise ValueError("Base URL is required")
        if not self.model_name:
            raise ValueError("Model name is required")
        if self.max_tokens <= 0:
            raise ValueError("Max tokens must be positive")
