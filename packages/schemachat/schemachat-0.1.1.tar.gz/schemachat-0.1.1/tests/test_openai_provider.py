"""
Unit tests for the OpenAI chat provider.
"""

import pytest
from unittest.mock import Mock, patch
from pydantic import BaseModel
from typing import List, Optional

from schemachat.core import OpenAIConfig
from schemachat.providers.openai import ChatOpenAI


class SampleResponseModel(BaseModel):
    """Sample model for structured responses."""
    name: str
    items: List[str] = []
    count: Optional[int] = None


class TestChatOpenAI:
    """Test cases for ChatOpenAI provider."""

    @pytest.fixture
    def openai_config(self):
        """Provide a valid OpenAI configuration."""
        return OpenAIConfig(
            api_key="test-api-key",
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1",
            fallback_model_name="gpt-3.5-turbo-fallback",
            max_tokens=1000,
            temperature=0.7
        )

    def test_init_valid_config(self, openai_config):
        """Test initialization with valid configuration."""
        provider = ChatOpenAI(openai_config)
        
        assert provider.config == openai_config
        assert provider._client is None  # Lazy initialization

    def test_init_invalid_config_type(self):
        """Test initialization with invalid configuration type."""
        # Using a dict instead of OpenAIConfig
        invalid_config = {"api_key": "test", "model_name": "gpt-3.5-turbo"}
        
        with pytest.raises(TypeError, match="Expected OpenAIConfig"):
            ChatOpenAI(invalid_config)

    def test_validate_config_missing_api_key(self):
        """Test validation failure with missing API key."""
        config = OpenAIConfig(
            api_key="",
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1",
            fallback_model_name=None
        )
        
        with pytest.raises(ValueError, match="API key is required"):
            ChatOpenAI(config)

    @patch('schemachat.providers.openai.OpenAI')
    def test_get_client_creates_client(self, mock_openai_class, openai_config):
        """Test that _get_client creates OpenAI client instance."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        provider = ChatOpenAI(openai_config)
        client = provider._get_client()
        
        assert client == mock_client
        mock_openai_class.assert_called_once_with(
            api_key=openai_config.api_key,
            base_url=openai_config.base_url
        )

    @patch('schemachat.providers.openai.OpenAI')
    def test_get_client_reuses_client(self, mock_openai_class, openai_config):
        """Test that _get_client reuses existing client instance."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        provider = ChatOpenAI(openai_config)
        client1 = provider._get_client()
        client2 = provider._get_client()
        
        assert client1 == client2
        mock_openai_class.assert_called_once()  # Called only once

    @patch('schemachat.providers.openai.OpenAI')
    def test_invoke_basic(self, mock_openai_class, openai_config):
        """Test basic text invocation."""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello, I'm a test response!"
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Test invocation
        provider = ChatOpenAI(openai_config)
        result = provider.invoke("Hello, how are you?", "You are a helpful assistant.")
        
        # Verify result
        assert result == "Hello, I'm a test response!"
        
        # Verify API call
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        
        assert call_kwargs["model"] == "gpt-3.5-turbo"
        assert call_kwargs["max_tokens"] == 1000
        assert call_kwargs["temperature"] == 0.7
        assert len(call_kwargs["messages"]) == 2
        assert call_kwargs["messages"][0]["role"] == "system"
        assert call_kwargs["messages"][0]["content"] == "You are a helpful assistant."
        assert call_kwargs["messages"][1]["role"] == "user"
        assert call_kwargs["messages"][1]["content"] == "Hello, how are you?"

    @patch('schemachat.providers.openai.OpenAI')
    def test_invoke_without_system_prompt(self, mock_openai_class, openai_config):
        """Test invocation without system prompt."""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response without system prompt"
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Test invocation
        provider = ChatOpenAI(openai_config)
        result = provider.invoke("What's the weather?")
        
        # Verify result
        assert result == "Response without system prompt"
        
        # Verify system prompt is empty
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["messages"][0]["content"] == ""

    @patch('schemachat.providers.openai.OpenAI')
    @patch('schemachat.providers.openai.ensure_json_format')
    def test_invoke_structured(self, mock_ensure_json, mock_openai_class, openai_config):
        """Test structured response invocation."""
        # Setup mocks
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"name": "test", "items": ["a", "b"]}'
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        expected_result = SampleResponseModel(name="test", items=["a", "b"])
        mock_ensure_json.return_value = expected_result
        
        # Test invocation
        provider = ChatOpenAI(openai_config)
        result = provider.invoke_structured(
            "Generate test data", 
            SampleResponseModel, 
            "You are a data generator"
        )
        
        # Verify result
        assert result == expected_result
        mock_ensure_json.assert_called_once_with(
            '{"name": "test", "items": ["a", "b"]}',
            SampleResponseModel
        )
        
        # Verify API call includes JSON schema instruction
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert len(call_kwargs["messages"]) == 3
        assert "JSON format" in call_kwargs["messages"][1]["content"]
        assert "schema" in call_kwargs["messages"][1]["content"]

    @patch('schemachat.providers.openai.OpenAI')
    def test_invoke_api_error(self, mock_openai_class, openai_config):
        """Test handling of API errors during invocation."""
        # Setup mock to raise exception
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client
        
        # Test that exception is propagated
        provider = ChatOpenAI(openai_config)
        with pytest.raises(Exception, match="API Error"):
            provider.invoke("Test message")

    def test_use_fallback_model_with_explicit_name(self, openai_config):
        """Test switching to fallback model with explicit name."""
        provider = ChatOpenAI(openai_config)
        original_model = provider.config.model_name
        
        provider.use_fallback_model("gpt-4")
        
        assert provider.config.model_name == "gpt-4"
        assert provider.config.model_name != original_model
        assert provider._client is None  # Client should be reset

    def test_use_fallback_model_with_config_fallback(self, openai_config):
        """Test switching to fallback model using config fallback."""
        provider = ChatOpenAI(openai_config)
        original_model = provider.config.model_name
        
        provider.use_fallback_model()
        
        assert provider.config.model_name == "gpt-3.5-turbo-fallback"
        assert provider.config.model_name != original_model
        assert provider._client is None

    def test_use_fallback_model_no_fallback_specified(self, openai_config):
        """Test fallback when no fallback is specified."""
        openai_config.fallback_model_name = None
        provider = ChatOpenAI(openai_config)
        
        with pytest.raises(ValueError, match="New model name must be provided"):
            provider.use_fallback_model()

    def test_get_provider_info(self, openai_config):
        """Test getting provider information."""
        provider = ChatOpenAI(openai_config)
        info = provider.get_provider_info()
        
        assert info["provider_type"] == "ChatOpenAI"
        assert info["model_name"] == "gpt-3.5-turbo"
        assert info["base_url"] == "https://api.openai.com/v1"
        assert info["max_tokens"] == 1000
        assert info["api_type"] == "OpenAI"

    def test_repr(self, openai_config):
        """Test string representation."""
        provider = ChatOpenAI(openai_config)
        repr_str = repr(provider)
        
        assert "ChatOpenAI" in repr_str
        assert "gpt-3.5-turbo" in repr_str