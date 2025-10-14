"""
Unit tests for the ChatProviderFactory.
"""

import pytest
from unittest.mock import Mock, patch
from schemachat.core import ProviderType, OpenAIConfig, OllamaConfig
from schemachat.providers.factory import ChatProviderFactory
from schemachat.providers.openai import ChatOpenAI
from schemachat.providers.ollama import ChatOllama


class TestChatProviderFactory:
    """Test cases for ChatProviderFactory."""

    def test_create_openai_provider(self):
        """Test creating an OpenAI provider."""
        config = OpenAIConfig(
            api_key="test-key",
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1",
            fallback_model_name=None
        )
        
        provider = ChatProviderFactory.create_provider(config)
        
        assert isinstance(provider, ChatOpenAI)
        assert provider.config == config

    def test_create_ollama_provider(self):
        """Test creating an Ollama provider."""
        config = OllamaConfig(
            model_name="llama2",
            base_url="http://localhost:11434",
            fallback_model_name=None
        )
        
        provider = ChatProviderFactory.create_provider(config)
        
        assert isinstance(provider, ChatOllama)
        assert provider.config == config

    def test_create_openrouter_provider(self):
        """Test creating an OpenRouter provider (uses OpenAI interface)."""
        config = OpenAIConfig(
            api_key="test-key",
            model_name="openrouter/model",
            base_url="https://openrouter.ai/api/v1",
            fallback_model_name=None
        )
        
        # Mock the config to return OPENROUTER provider type
        with patch.object(config, 'get_provider_type', return_value=ProviderType.OPENROUTER):
            provider = ChatProviderFactory.create_provider(config)
            
            # Should create ChatOpenAI instance since OPENROUTER uses OpenAI interface
            assert isinstance(provider, ChatOpenAI)
            assert provider.config == config

    def test_create_provider_validates_config(self):
        """Test that factory validates configuration before creating provider."""
        # Create invalid config (missing API key)
        config = OpenAIConfig(
            api_key="",
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1",
            fallback_model_name=None
        )
        
        with pytest.raises(ValueError, match="API key is required"):
            ChatProviderFactory.create_provider(config)

    def test_create_provider_unsupported_type(self):
        """Test creating provider with unsupported type."""
        # Mock config with unsupported provider type
        mock_config = Mock()
        mock_config.validate.return_value = None
        mock_config.get_provider_type.return_value = "unsupported_type"
        
        with pytest.raises(ValueError, match="Unsupported provider type"):
            ChatProviderFactory.create_provider(mock_config)

    def test_get_supported_providers(self):
        """Test getting all supported provider types."""
        supported = ChatProviderFactory.get_supported_providers()
        
        assert ProviderType.OPENAI in supported
        assert ProviderType.OLLAMA in supported
        assert ProviderType.OPENROUTER in supported
        
        # Verify the classes are correct
        assert supported[ProviderType.OPENAI] == ChatOpenAI
        assert supported[ProviderType.OLLAMA] == ChatOllama
        assert supported[ProviderType.OPENROUTER] == ChatOpenAI  # Uses OpenAI interface

    def test_get_supported_providers_returns_copy(self):
        """Test that get_supported_providers returns a copy, not the original."""
        supported1 = ChatProviderFactory.get_supported_providers()
        supported2 = ChatProviderFactory.get_supported_providers()
        
        # Should be equal but not the same object
        assert supported1 == supported2
        assert supported1 is not supported2
        
        # Modifying one shouldn't affect the other
        supported1.clear()
        supported2_after = ChatProviderFactory.get_supported_providers()
        assert len(supported2_after) > 0

    def test_is_provider_supported_true(self):
        """Test is_provider_supported with supported types."""
        assert ChatProviderFactory.is_provider_supported(ProviderType.OPENAI) == True
        assert ChatProviderFactory.is_provider_supported(ProviderType.OLLAMA) == True
        assert ChatProviderFactory.is_provider_supported(ProviderType.OPENROUTER) == True

    def test_is_provider_supported_false(self):
        """Test is_provider_supported with unsupported type."""
        # This would require creating a new ProviderType that's not in the registry
        # For now, we'll test with a string that's not a valid provider type
        # Note: This test might need adjustment based on actual implementation
        class UnsupportedType:
            pass
        
        assert ChatProviderFactory.is_provider_supported(UnsupportedType()) == False

    @patch('schemachat.providers.factory.logger')
    def test_create_provider_logs_debug(self, mock_logger):
        """Test that provider creation logs debug information."""
        config = OpenAIConfig(
            api_key="test-key",
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1",
            fallback_model_name=None
        )
        
        provider = ChatProviderFactory.create_provider(config)
        
        # Verify debug logging was called
        mock_logger.debug.assert_called_once()
        call_args = mock_logger.debug.call_args[0][0]
        assert "Creating ChatOpenAI" in call_args
        assert "config:" in call_args