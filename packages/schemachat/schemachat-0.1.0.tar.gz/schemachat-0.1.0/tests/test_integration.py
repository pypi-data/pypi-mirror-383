"""
Integration tests for the schemachat system.
"""

import pytest
from unittest.mock import Mock, patch
from pydantic import BaseModel
from typing import List

from core import OpenAIConfig, OllamaConfig, ProviderType
from providers.factory import ChatProviderFactory


class UserProfile(BaseModel):
    """Test model for integration testing."""
    name: str
    age: int
    skills: List[str] = []


class TestIntegration:
    """Integration tests for the complete system."""

    @pytest.fixture
    def openai_config(self):
        """Valid OpenAI configuration for testing."""
        return OpenAIConfig(
            api_key="test-openai-key",
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1",
            fallback_model_name=None,
            max_tokens=2000,
            temperature=0.8
        )

    @pytest.fixture
    def ollama_config(self):
        """Valid Ollama configuration for testing."""
        return OllamaConfig(
            model_name="llama2",
            base_url="http://localhost:11434",
            fallback_model_name=None,
            max_num_ctx=256,
            num_predict=1024
        )

    @patch('providers.openai.OpenAI')
    def test_openai_end_to_end_text_generation(self, mock_openai_class, openai_config):
        """Test complete OpenAI text generation flow."""
        # Setup mock response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is a comprehensive test response from OpenAI."
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Create provider using factory
        provider = ChatProviderFactory.create_provider(openai_config)
        
        # Test text generation
        result = provider.invoke(
            "Write a comprehensive test message",
            "You are a testing assistant."
        )
        
        # Verify result
        assert result == "This is a comprehensive test response from OpenAI."
        assert "comprehensive" in result
        
        # Verify provider info
        info = provider.get_provider_info()
        assert info["provider_type"] == "ChatOpenAI"
        assert info["model_name"] == "gpt-3.5-turbo"

    @patch('providers.openai.OpenAI')
    @patch('providers.openai.ensure_json_format')
    def test_openai_end_to_end_structured_generation(self, mock_ensure_json, mock_openai_class, openai_config):
        """Test complete OpenAI structured generation flow."""
        # Setup mocks
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"name": "Alice Smith", "age": 30, "skills": ["Python", "Testing"]}'
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        expected_profile = UserProfile(name="Alice Smith", age=30, skills=["Python", "Testing"])
        mock_ensure_json.return_value = expected_profile
        
        # Create provider using factory
        provider = ChatProviderFactory.create_provider(openai_config)
        
        # Test structured generation
        result = provider.invoke_structured(
            "Generate a user profile for a software developer",
            UserProfile,
            "You are a profile generator."
        )
        
        # Verify result
        assert isinstance(result, UserProfile)
        assert result.name == "Alice Smith"
        assert result.age == 30
        assert "Python" in result.skills
        assert "Testing" in result.skills

    @patch('providers.ollama.ollama.Client')
    def test_ollama_end_to_end_text_generation(self, mock_ollama_client, ollama_config):
        """Test complete Ollama text generation flow."""
        # Setup mock response
        mock_client_instance = Mock()
        mock_client_instance.chat.return_value = {
            "message": {"content": "This is a comprehensive test response from Ollama."}
        }
        mock_ollama_client.return_value = mock_client_instance
        
        # Create provider using factory
        provider = ChatProviderFactory.create_provider(ollama_config)
        
        # Test text generation
        result = provider.invoke(
            "Write a comprehensive test message",
            "You are a testing assistant."
        )
        
        # Verify result
        assert result == "This is a comprehensive test response from Ollama."
        assert "comprehensive" in result
        
        # Verify provider info
        info = provider.get_provider_info()
        assert info["provider_type"] == "ChatOllama"
        assert info["model_name"] == "llama2"
        assert info["api_type"] == "Ollama"

    @patch('providers.ollama.ollama.Client')
    @patch('providers.ollama.ensure_json_format')
    def test_ollama_end_to_end_structured_generation(self, mock_ensure_json, mock_ollama_client, ollama_config):
        """Test complete Ollama structured generation flow."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client_instance.chat.return_value = {
            "message": {"content": '{"name": "Bob Johnson", "age": 25, "skills": ["Go", "Docker"]}'}
        }
        mock_ollama_client.return_value = mock_client_instance
        
        expected_profile = UserProfile(name="Bob Johnson", age=25, skills=["Go", "Docker"])
        mock_ensure_json.return_value = expected_profile
        
        # Create provider using factory
        provider = ChatProviderFactory.create_provider(ollama_config)
        
        # Test structured generation
        result = provider.invoke_structured(
            "Generate a user profile for a DevOps engineer",
            UserProfile,
            "You are a profile generator."
        )
        
        # Verify result
        assert isinstance(result, UserProfile)
        assert result.name == "Bob Johnson"
        assert result.age == 25
        assert "Go" in result.skills
        assert "Docker" in result.skills

    def test_factory_supports_all_provider_types(self):
        """Test that factory supports all defined provider types."""
        supported = ChatProviderFactory.get_supported_providers()
        
        # Verify all enum values are supported
        for provider_type in ProviderType:
            assert provider_type in supported
            assert supported[provider_type] is not None

    @patch('providers.openai.OpenAI')
    def test_fallback_model_switching_workflow(self, mock_openai_class, openai_config):
        """Test complete workflow with fallback model switching."""
        # Setup initial success, then failure, then fallback success
        mock_client = Mock()
        mock_responses = [
            # First call succeeds
            Mock(choices=[Mock(message=Mock(content="Initial response"))]),
            # Second call fails
            Exception("Model overloaded"),
            # Third call succeeds with fallback
            Mock(choices=[Mock(message=Mock(content="Fallback response"))])
        ]
        
        mock_client.chat.completions.create.side_effect = mock_responses
        mock_openai_class.return_value = mock_client
        
        # Add fallback model to config
        openai_config.fallback_model_name = "gpt-3.5-turbo-fallback"
        
        # Create provider
        provider = ChatProviderFactory.create_provider(openai_config)
        
        # First call should succeed
        result1 = provider.invoke("Test message 1")
        assert result1 == "Initial response"
        assert provider.config.model_name == "gpt-3.5-turbo"
        
        # Second call should fail
        with pytest.raises(Exception, match="Model overloaded"):
            provider.invoke("Test message 2")
        
        # Switch to fallback model
        provider.use_fallback_model()
        assert provider.config.model_name == "gpt-3.5-turbo-fallback"
        
        # Third call should succeed with fallback
        result3 = provider.invoke("Test message 3")
        assert result3 == "Fallback response"

    def test_config_validation_in_factory_workflow(self):
        """Test that configuration validation works in complete workflow."""
        # Test with invalid OpenAI config
        invalid_openai_config = OpenAIConfig(
            api_key="",  # Invalid: empty API key
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1",
            fallback_model_name=None
        )
        
        with pytest.raises(ValueError, match="API key is required"):
            ChatProviderFactory.create_provider(invalid_openai_config)
        
        # Test with invalid Ollama config
        invalid_ollama_config = OllamaConfig(
            model_name="",  # Invalid: empty model name
            base_url="http://localhost:11434",
            fallback_model_name=None
        )
        
        with pytest.raises(ValueError, match="Model name is required"):
            ChatProviderFactory.create_provider(invalid_ollama_config)

    def test_provider_type_consistency(self, openai_config, ollama_config):
        """Test that provider types are consistent across the system."""
        # Test OpenAI
        openai_provider = ChatProviderFactory.create_provider(openai_config)
        assert openai_config.get_provider_type() == ProviderType.OPENAI
        assert "OpenAI" in openai_provider.__class__.__name__
        
        # Test Ollama
        ollama_provider = ChatProviderFactory.create_provider(ollama_config)
        assert ollama_config.get_provider_type() == ProviderType.OLLAMA
        assert "Ollama" in ollama_provider.__class__.__name__
        
        # Test provider info consistency
        openai_info = openai_provider.get_provider_info()
        ollama_info = ollama_provider.get_provider_info()
        
        assert "provider_type" in openai_info
        assert "provider_type" in ollama_info
        assert "model_name" in openai_info
        assert "model_name" in ollama_info

    @patch('providers.openai.OpenAI')
    def test_multiple_invocations_same_provider(self, mock_openai_class, openai_config):
        """Test multiple invocations with the same provider instance."""
        # Setup mock to return different responses
        mock_client = Mock()
        responses = [
            Mock(choices=[Mock(message=Mock(content="Response 1"))]),
            Mock(choices=[Mock(message=Mock(content="Response 2"))]),
            Mock(choices=[Mock(message=Mock(content="Response 3"))])
        ]
        mock_client.chat.completions.create.side_effect = responses
        mock_openai_class.return_value = mock_client
        
        # Create provider
        provider = ChatProviderFactory.create_provider(openai_config)
        
        # Make multiple calls
        result1 = provider.invoke("Message 1")
        result2 = provider.invoke("Message 2")
        result3 = provider.invoke("Message 3")
        
        # Verify all responses
        assert result1 == "Response 1"
        assert result2 == "Response 2"
        assert result3 == "Response 3"
        
        # Verify client was reused (created only once)
        mock_openai_class.assert_called_once()
        
        # Verify all API calls were made
        assert mock_client.chat.completions.create.call_count == 3