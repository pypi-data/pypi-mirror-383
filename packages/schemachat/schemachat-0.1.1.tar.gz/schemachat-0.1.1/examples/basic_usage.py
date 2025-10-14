"""
Basic usage examples for SchemaChat.

This file demonstrates how to use the SchemaChat library with different providers
and both text generation and structured output modes.
"""

from typing import List
from pydantic import BaseModel

# Import SchemaChat components
from schemachat.core.configs.openai import OpenAIConfig
from schemachat.core.configs.ollama import OllamaConfig
from schemachat.providers.factory import ChatProviderFactory


# Example Pydantic model for structured output
class PersonProfile(BaseModel):
    name: str
    age: int
    profession: str
    skills: List[str]
    bio: str


def example_openai_text_generation():
    """Example of basic text generation with OpenAI."""
    print("=== OpenAI Text Generation Example ===")
    
    config = OpenAIConfig(
        api_key="your-openai-api-key-here",  # Replace with actual API key
        base_url="https://api.openai.com/v1",
        model_name="gpt-3.5-turbo",
        fallback_model_name="gpt-4",
        temperature=0.7
    )
    
    try:
        client = ChatProviderFactory.create_provider(config)
        
        # Basic text generation
        response = client.invoke(
            "Explain what machine learning is in simple terms.",
            system="You are a helpful AI assistant that explains complex topics clearly."
        )
        
        print(f"Response: {response}")
        
        # Get provider information
        info = client.get_provider_info()
        print(f"Using: {info['provider_type']} with model {info['model_name']}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Make sure to set a valid OpenAI API key")


def example_openai_structured_output():
    """Example of structured output generation with OpenAI."""
    print("\n=== OpenAI Structured Output Example ===")
    
    config = OpenAIConfig(
        api_key="your-openai-api-key-here",  # Replace with actual API key
        base_url="https://api.openai.com/v1",
        model_name="gpt-3.5-turbo",
        fallback_model_name="gpt-4"
    )
    
    try:
        client = ChatProviderFactory.create_provider(config)
        
        # Structured output generation
        person = client.invoke_structured(
            "Create a profile for a senior Python developer with 5 years of experience",
            response_model=PersonProfile,
            system="Generate realistic professional profiles based on the request."
        )
        
        print(f"Generated Profile:")
        print(f"  Name: {person.name}")
        print(f"  Age: {person.age}")
        print(f"  Profession: {person.profession}")
        print(f"  Skills: {', '.join(person.skills)}")
        print(f"  Bio: {person.bio}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Make sure to set a valid OpenAI API key")


def example_ollama_usage():
    """Example of using Ollama provider."""
    print("\n=== Ollama Usage Example ===")
    
    config = OllamaConfig(
        base_url="http://localhost:11434",
        model_name="llama3.1",
        fallback_model_name="llama3",
        max_num_ctx=128,  # 128KB context
        num_predict=2048
    )
    
    try:
        client = ChatProviderFactory.create_provider(config)
        
        # Basic text generation
        response = client.invoke(
            "What are the benefits of using Python for data science?",
            system="You are a knowledgeable data science expert."
        )
        
        print(f"Ollama Response: {response}")
        
        # Show provider info
        info = client.get_provider_info()
        print(f"Context size: {info['max_context_tokens']} tokens")
        print(f"Model: {info['model_name']}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Make sure Ollama is running locally with the specified model")


def example_model_fallback():
    """Example of using model fallback functionality."""
    print("\n=== Model Fallback Example ===")
    
    config = OpenAIConfig(
        api_key="your-openai-api-key-here",
        base_url="https://api.openai.com/v1",
        model_name="gpt-4",
        fallback_model_name="gpt-3.5-turbo"
    )
    
    try:
        client = ChatProviderFactory.create_provider(config)
        
        print(f"Original model: {client.get_provider_info()['model_name']}")
        
        # Switch to fallback model
        client.use_fallback_model()
        print(f"After fallback: {client.get_provider_info()['model_name']}")
        
        # Switch to specific model
        client.use_fallback_model("gpt-4-turbo")
        print(f"After specific switch: {client.get_provider_info()['model_name']}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("SchemaChat Usage Examples")
    print("=" * 40)
    
    # Run examples
    example_openai_text_generation()
    example_openai_structured_output()
    example_ollama_usage()
    example_model_fallback()
    
    print("\n" + "=" * 40)
    print("Examples completed!")
    print("\nTo use these examples:")
    print("1. Replace 'your-openai-api-key-here' with your actual OpenAI API key")
    print("2. Ensure Ollama is running locally for Ollama examples")
    print("3. Install required models in Ollama (e.g., 'ollama pull llama3.1')")
