"""
Unit tests for configuration classes.
"""

import pytest
from schemachat.core import BaseConfig, ProviderType, OpenAIConfig, OllamaConfig


class TestOpenAIConfig:
    """Test cases for OpenAIConfig."""

    def test_valid_config_creation(self):
        """Test creating a valid OpenAI configuration."""
        config = OpenAIConfig(
            api_key="test-key",
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1",
            fallback_model_name=None
        )
        
        assert config.api_key == "test-key"
        assert config.model_name == "gpt-3.5-turbo"
        assert config.base_url == "https://api.openai.com/v1"
        assert config.max_tokens == 8192  # default value
        assert config.get_provider_type() == ProviderType.OPENAI

    def test_config_validation_success(self):
        """Test successful configuration validation."""
        config = OpenAIConfig(
            api_key="test-key",
            model_name="gpt-4",
            base_url="https://api.openai.com/v1",
            fallback_model_name=None
        )
        
        # Should not raise an exception
        config.validate()

    def test_config_validation_missing_api_key(self):
        """Test validation failure with missing API key."""
        config = OpenAIConfig(
            api_key="",
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1",
            fallback_model_name=None
        )
        
        with pytest.raises(ValueError, match="API key is required"):
            config.validate()

    def test_config_validation_missing_base_url(self):
        """Test validation failure with missing base URL."""
        config = OpenAIConfig(
            api_key="test-key",
            model_name="gpt-3.5-turbo",
            base_url="",
            fallback_model_name=None
        )
        
        with pytest.raises(ValueError, match="Base URL is required"):
            config.validate()

    def test_config_validation_missing_model_name(self):
        """Test validation failure with missing model name."""
        config = OpenAIConfig(
            api_key="test-key",
            model_name="",
            base_url="https://api.openai.com/v1",
            fallback_model_name=None
        )
        
        with pytest.raises(ValueError, match="Model name is required"):
            config.validate()

    def test_config_validation_invalid_max_tokens(self):
        """Test validation failure with invalid max tokens."""
        config = OpenAIConfig(
            api_key="test-key",
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1",
            fallback_model_name=None,
            max_tokens=0
        )
        
        with pytest.raises(ValueError, match="Max tokens must be positive"):
            config.validate()

    def test_config_to_dict(self):
        """Test configuration dictionary conversion."""
        config = OpenAIConfig(
            api_key="test-key",
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1",
            fallback_model_name="gpt-3.5-turbo-fallback",
            max_tokens=4000,
            temperature=0.7
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["api_key"] == "test-key"
        assert config_dict["model_name"] == "gpt-3.5-turbo"
        assert config_dict["base_url"] == "https://api.openai.com/v1"
        assert config_dict["fallback_model_name"] == "gpt-3.5-turbo-fallback"
        assert config_dict["max_tokens"] == 4000
        assert config_dict["temperature"] == 0.7


class TestOllamaConfig:
    """Test cases for OllamaConfig."""

    def test_valid_config_creation(self):
        """Test creating a valid Ollama configuration."""
        config = OllamaConfig(
            model_name="llama2",
            base_url="http://localhost:11434",
            fallback_model_name=None
        )
        
        assert config.model_name == "llama2"
        assert config.base_url == "http://localhost:11434"
        assert config.max_num_ctx == 128  # default value
        assert config.get_provider_type() == ProviderType.OLLAMA

    def test_config_validation_success(self):
        """Test successful configuration validation."""
        config = OllamaConfig(
            model_name="llama2",
            base_url="http://localhost:11434",
            fallback_model_name=None
        )
        
        # Should not raise an exception
        config.validate()

    def test_config_validation_missing_base_url(self):
        """Test validation failure with missing base URL."""
        config = OllamaConfig(
            model_name="llama2",
            base_url="",
            fallback_model_name=None
        )
        
        with pytest.raises(ValueError, match="Base URL is required"):
            config.validate()

    def test_config_validation_missing_model_name(self):
        """Test validation failure with missing model name."""
        config = OllamaConfig(
            model_name="",
            base_url="http://localhost:11434",
            fallback_model_name=None
        )
        
        with pytest.raises(ValueError, match="Model name is required"):
            config.validate()

    def test_config_validation_invalid_max_num_ctx(self):
        """Test validation failure with invalid max context size."""
        config = OllamaConfig(
            model_name="llama2",
            base_url="http://localhost:11434",
            fallback_model_name=None,
            max_num_ctx=0
        )
        
        with pytest.raises(ValueError, match="Max context size must be positive"):
            config.validate()

    def test_get_max_context_tokens(self):
        """Test max context tokens calculation."""
        config = OllamaConfig(
            model_name="llama2",
            base_url="http://localhost:11434",
            fallback_model_name=None,
            max_num_ctx=64
        )
        
        # 64 KB * 1024 = 65536 tokens
        assert config.get_max_context_tokens() == 65536

    def test_config_to_dict(self):
        """Test configuration dictionary conversion."""
        config = OllamaConfig(
            model_name="llama2",
            base_url="http://localhost:11434",
            fallback_model_name="llama2-fallback",
            max_num_ctx=256,
            num_ctx=8192,
            num_predict=2048
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["model_name"] == "llama2"
        assert config_dict["base_url"] == "http://localhost:11434"
        assert config_dict["fallback_model_name"] == "llama2-fallback"
        assert config_dict["max_num_ctx"] == 256
        assert config_dict["num_ctx"] == 8192
        assert config_dict["num_predict"] == 2048


class TestProviderType:
    """Test cases for ProviderType enum."""

    def test_provider_type_values(self):
        """Test all provider type enum values."""
        assert ProviderType.OPENAI.value == "openai"
        assert ProviderType.OLLAMA.value == "ollama"
        assert ProviderType.OPENROUTER.value == "openrouter"

    def test_provider_type_comparison(self):
        """Test provider type comparisons."""
        assert ProviderType.OPENAI == ProviderType.OPENAI
        assert ProviderType.OPENAI != ProviderType.OLLAMA
        assert ProviderType.OLLAMA != ProviderType.OPENROUTER