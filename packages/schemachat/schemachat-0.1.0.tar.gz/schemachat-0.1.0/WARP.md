# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Development Commands

### Environment Setup
- **Install dependencies**: `uv sync`
- **Add new dependencies**: `uv add <package-name>`
- **Remove dependencies**: `uv remove <package-name>`
- **Create virtual environment**: `uv venv`

### Running the Application
- **Run main application**: `python main.py`
- **Run with uv**: `uv run python main.py`

### Development Tools
- **Update lockfile**: `uv lock`
- **Export dependencies**: `uv export`
- **View dependency tree**: `uv tree`
- **Build package**: `uv build`

### Python Environment
- **Current Python version**: 3.10 (specified in `.python-version`)
- **Manage Python versions**: `uv python install <version>`

## Architecture Overview

### Core Design Pattern
This is a **multi-provider chat abstraction library** that implements a factory pattern to support different LLM providers (OpenAI, Ollama, OpenRouter) through a unified interface.

### Key Architectural Components

#### 1. **Provider Abstraction Layer** (`core/`)
- `BaseLLMClient`: Abstract base class defining the interface for all chat providers
- `BaseConfig`: Abstract configuration base for provider-specific settings
- `ProviderType`: Enum defining supported provider types (OpenAI, Ollama, OpenRouter)

#### 2. **Configuration System** (`core/configs/`)
- Provider-specific configuration classes inherit from `BaseConfig`
- `OllamaConfig`: Handles context size management, token calculations
- `OpenAIConfig`: Manages API keys, model parameters (temperature, top_p, max_tokens)

#### 3. **Provider Implementations** (`providers/`)
- `ChatOpenAI`: OpenAI-compatible API implementation
- `ChatOllama`: Ollama API implementation with advanced context management
- `ChatProviderFactory`: Factory class for creating provider instances

#### 4. **Utility Functions** (`core/utils.py`)
- `ensure_json_format()`: Handles JSON parsing and validation for structured outputs

### Key Features

#### Dual Response Modes
- **Text Generation**: `invoke()` method for plain text responses
- **Structured Output**: `invoke_structured()` method with Pydantic model validation

#### Provider-Specific Optimizations
- **Ollama**: Advanced context size optimization with token calculation and tiered context management
- **OpenAI**: Standard API integration with configurable parameters

#### Configuration Management
- Each provider validates its own configuration requirements
- Fallback model support for provider switching
- Provider introspection via `get_provider_info()`

### Dependencies
- **ollama**: Ollama API client
- **openai**: OpenAI API client  
- **pydantic**: Data validation and structured output
- **tiktoken**: Token counting for Ollama context optimization

### Usage Pattern
```python
from core.configs.openai import OpenAIConfig
from providers.factory import ChatProviderFactory

config = OpenAIConfig(
    api_key="your-key",
    base_url="https://api.openai.com/v1",
    model_name="gpt-4"
)

client = ChatProviderFactory.create_provider(config)
response = client.invoke("Hello, world!")
```

### Important Implementation Details
- **Context Management**: Ollama provider includes sophisticated context size calculation and optimization
- **Error Handling**: Structured response parsing includes fallback JSON extraction
- **Provider Registry**: Factory maintains a registry of supported providers for easy extension
- **Configuration Validation**: Each config class implements provider-specific validation logic
