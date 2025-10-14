# SchemaChat

A unified Python interface for multiple LLM chat providers with structured output support using Pydantic models.

## Features

- **Multi-provider support**: OpenAI, Ollama, and OpenRouter APIs
- **Structured output**: Generate validated responses using Pydantic models
- **Factory pattern**: Easy provider instantiation and switching
- **Advanced context management**: Intelligent context size optimization for Ollama
- **Fallback model support**: Switch models dynamically for error recovery
- **Type safety**: Full type hints and validation throughout

## Installation

```bash
pip install schemachat
```

## Quick Start

### Basic Text Generation

```python
from schemachat.core.configs.openai import OpenAIConfig
from schemachat.providers.factory import ChatProviderFactory

# Configure OpenAI provider
config = OpenAIConfig(
    api_key="your-openai-api-key",
    base_url="https://api.openai.com/v1",
    model_name="gpt-4",
    fallback_model_name="gpt-3.5-turbo"
)

# Create provider instance
client = ChatProviderFactory.create_provider(config)

# Generate response
response = client.invoke("Hello, world!")
print(response)
```

### Structured Output Generation

```python
from pydantic import BaseModel
from typing import List

class Person(BaseModel):
    name: str
    age: int
    skills: List[str]

# Generate structured response
person = client.invoke_structured(
    "Generate a profile for a Python developer",
    response_model=Person
)

print(f"Name: {person.name}")
print(f"Age: {person.age}")
print(f"Skills: {', '.join(person.skills)}")
```

### Using Ollama Provider

```python
from schemachat.core.configs.ollama import OllamaConfig

# Configure Ollama provider
config = OllamaConfig(
    base_url="http://localhost:11434",
    model_name="llama3.1",
    fallback_model_name="llama3",
    max_num_ctx=128,  # Context size in KB
    num_predict=8192  # Max prediction tokens
)

client = ChatProviderFactory.create_provider(config)
response = client.invoke("Explain quantum computing")
```

## Supported Providers

### OpenAI (and OpenAI-compatible APIs)
- Official OpenAI API
- OpenRouter
- Any OpenAI-compatible endpoint

### Ollama
- Local Ollama installations
- Advanced context size management
- Automatic token calculation and optimization

## Architecture

SchemaChat uses a factory pattern with provider-specific implementations:

- **`BaseLLMClient`**: Abstract interface for all providers
- **`BaseConfig`**: Configuration base class with validation
- **`ChatProviderFactory`**: Factory for creating provider instances
- **Provider-specific optimizations**: Each provider includes tailored optimizations

## Configuration Options

### OpenAI Configuration
```python
OpenAIConfig(
    api_key="your-key",
    base_url="https://api.openai.com/v1",
    model_name="gpt-4",
    fallback_model_name="gpt-3.5-turbo",
    max_tokens=8192,
    temperature=0.7,
    top_p=0.9
)
```

### Ollama Configuration
```python
OllamaConfig(
    base_url="http://localhost:11434",
    model_name="llama3.1",
    fallback_model_name="llama3",
    max_num_ctx=128,  # KB
    num_ctx=32768,    # Specific context size
    num_predict=8192  # Max prediction tokens
)
```

## Advanced Features

### Provider Information
```python
info = client.get_provider_info()
print(f"Provider: {info['provider_type']}")
print(f"Model: {info['model_name']}")
print(f"Base URL: {info['base_url']}")
```

### Model Switching
```python
# Switch to fallback model
client.use_fallback_model()

# Switch to specific model
client.use_fallback_model("gpt-4-turbo")
```

### Error Handling
```python
try:
    response = client.invoke("Your prompt")
except Exception as e:
    print(f"Error: {e}")
    # Automatically try fallback model
    client.use_fallback_model()
    response = client.invoke("Your prompt")
```

## Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/yourusername/schemachat.git
cd schemachat

# Install dependencies
uv sync

# Install development dependencies
uv sync --group dev
```

### Running Tests
```bash
uv run pytest
```

### Code Formatting
```bash
uv run black .
uv run ruff check .
```

### Type Checking
```bash
uv run mypy .
```

## Requirements

- Python 3.10+
- pydantic>=2.12.0
- openai>=2.3.0 (for OpenAI providers)
- ollama>=0.6.0 (for Ollama providers)
- tiktoken>=0.12.0 (for token counting)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
