"""
Test configuration and fixtures for schemachat tests.
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, MagicMock

from core import BaseConfig, ProviderType, OpenAIConfig, OllamaConfig


class MockConfig(BaseConfig):
    """Mock configuration for testing."""
    
    def __init__(self, base_url: str = "http://test", model_name: str = "test-model", 
                 fallback_model_name: str = None):
        self.base_url = base_url
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
    
    def get_provider_type(self) -> ProviderType:
        return ProviderType.OPENAI
    
    def validate(self) -> None:
        if not self.base_url:
            raise ValueError("base_url is required")
        if not self.model_name:
            raise ValueError("model_name is required")


@pytest.fixture
def mock_config():
    """Provide a mock configuration for testing."""
    return MockConfig()


@pytest.fixture
def openai_config():
    """Provide an OpenAI configuration for testing."""
    return OpenAIConfig(
        api_key="test-key",
        model_name="gpt-3.5-turbo",
        base_url="https://api.openai.com/v1",
        max_tokens=1000,
        temperature=0.7
    )


@pytest.fixture
def ollama_config():
    """Provide an Ollama configuration for testing."""
    return OllamaConfig(
        model_name="llama2",
        base_url="http://localhost:11434",
        max_num_ctx=128,
        num_predict=1024
    )


@pytest.fixture
def mock_openai_client():
    """Provide a mock OpenAI client."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Test response"
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_ollama_client():
    """Provide a mock Ollama client."""
    mock_client = Mock()
    mock_client.chat.return_value = {
        "message": {"content": "Test response"}
    }
    return mock_client


@pytest.fixture
def sample_messages():
    """Provide sample test messages."""
    return {
        "simple": "Hello, how are you?",
        "complex": "Analyze the following data and provide insights: [1, 2, 3, 4, 5]",
        "empty": "",
        "long": "This is a very long message " * 100
    }


@pytest.fixture
def sample_system_prompts():
    """Provide sample system prompts."""
    return {
        "helpful": "You are a helpful assistant.",
        "analytical": "You are an analytical assistant that provides detailed insights.",
        "empty": "",
        "json": "Always respond with valid JSON format."
    }