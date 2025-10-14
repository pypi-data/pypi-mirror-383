# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Install dependencies using uv (preferred package manager)
uv sync

# Install with development dependencies
uv sync --group dev
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_configs.py

# Run specific test function
uv run pytest tests/test_integration.py::test_openai_structured_output -v
```

### Code Quality
```bash
# Format code
uv run black .

# Check linting
uv run ruff check .

# Type checking
uv run mypy .
```

### Running Examples
```bash
# Run basic usage examples
uv run python examples/basic_usage.py

# Run main entry point
uv run python main.py
```

## Architecture Overview

SchemaChat is a unified Python interface for multiple LLM chat providers with structured output support. The codebase follows a factory pattern architecture:

### Core Components

**Factory Pattern Implementation:**
- `ChatProviderFactory` creates provider instances based on configuration type
- `BaseLLMClient` abstract interface defines common API for all providers
- `BaseConfig` base class with validation for all provider configurations

**Provider Structure:**
- `ChatOpenAI` - OpenAI and OpenAI-compatible APIs (OpenRouter)
- `ChatOllama` - Local Ollama installations with context management
- Each provider implements both text generation (`invoke`) and structured output (`invoke_structured`)

**Configuration System:**
- `OpenAIConfig` - API key, model selection, fallback models
- `OllamaConfig` - Local URL, context size management, token optimization
- All configs support model switching and fallback mechanisms

### Key Design Patterns

**Provider Registration:**
```python
_providers: Dict[ProviderType, Type[BaseLLMClient]] = {
    ProviderType.OPENAI: ChatOpenAI,
    ProviderType.OLLAMA: ChatOllama,
    ProviderType.OPENROUTER: ChatOpenAI,  # Reuses OpenAI interface
}
```

**Structured Output Flow:**
1. User provides Pydantic model class as `response_model`
2. Provider generates JSON following model schema
3. Response is validated and returned as typed model instance

**Context Management (Ollama-specific):**
- Automatic token counting using tiktoken
- Dynamic context size optimization based on `max_num_ctx` (in KB)
- Intelligent message truncation to fit context limits

### File Structure Logic

- `core/` - Base classes and configuration definitions
- `providers/` - Concrete provider implementations
- `examples/` - Usage demonstrations for all supported patterns
- `tests/` - Comprehensive test coverage including integration tests

## Python Environment

- **Python Version**: 3.10+ (specified in `.python-version`)
- **Package Manager**: uv (preferred for dependency management)
- **Build System**: Hatchling

## Testing Strategy

The test suite includes:
- **Unit tests** for configurations and individual components
- **Integration tests** with mocked API responses
- **Factory tests** for provider instantiation and switching
- **Utility tests** for token counting and context management

Tests use pytest with fixtures defined in `conftest.py` for shared test configurations.

## Provider-Specific Notes

**OpenAI Provider:**
- Supports both OpenAI API and OpenRouter endpoints
- Implements structured output via JSON schema validation
- Includes automatic fallback model switching on errors

**Ollama Provider:**
- Advanced context size management with automatic token calculation
- Converts KB-based `max_num_ctx` to token limits
- Optimized for local model deployments

**Factory Pattern:**
- Automatic provider selection based on config type
- Registry-based provider lookup for extensibility
- Consistent error handling across all provider types
