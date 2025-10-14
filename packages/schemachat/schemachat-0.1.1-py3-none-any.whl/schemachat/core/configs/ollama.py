from dataclasses import dataclass
from typing import Optional

from ..base_config import BaseConfig, ProviderType


@dataclass
class OllamaConfig(BaseConfig):
    """Configuration for Ollama providers."""

    max_num_ctx: int = 128  # In KB
    num_ctx: Optional[int] = None
    num_predict: Optional[int] = None

    def get_provider_type(self) -> ProviderType:
        return ProviderType.OLLAMA

    def validate(self) -> None:
        if not self.base_url:
            raise ValueError("Base URL is required")
        if not self.model_name:
            raise ValueError("Model name is required")
        if self.max_num_ctx <= 0:
            raise ValueError("Max context size must be positive")

    def get_max_context_tokens(self) -> int:
        """Get maximum context size in tokens."""
        return self.max_num_ctx * 1024
