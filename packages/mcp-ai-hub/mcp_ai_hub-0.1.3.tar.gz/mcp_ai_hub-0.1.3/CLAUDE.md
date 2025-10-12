# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP AI Hub is a Model Context Protocol (MCP) server that provides unified access to 100+ AI providers through LiteLM. It acts as a bridge between MCP clients (like Claude Desktop/Code) and multiple AI providers including OpenAI, Anthropic, Google, Azure, AWS Bedrock, and more.

## Core Architecture

The project follows a clean, modular architecture:

```
src/mcp_ai_hub/
├── __init__.py          # Package metadata and version
├── server.py            # FastMCP server implementation with MCP tools
├── ai_client.py         # LiteLM wrapper for unified AI provider access
└── config.py            # Pydantic configuration models for YAML validation
```

**Data Flow:**
```
MCP Client → FastMCP Server → AIClient → LiteLM → AI Provider APIs
```

## Development Commands

### Setup and Dependencies
```bash
# Install all dependencies including dev dependencies
uv sync

# Install package in development mode
uv pip install -e .

# Add new runtime dependencies
uv add package_name

# Add new development dependencies
uv add --dev package_name
```

### Running the Server
```bash
# Run with stdio transport (default for MCP clients)
uv run python -m mcp_ai_hub.server

# Run with custom configuration and debug logging
uv run python -m mcp_ai_hub.server --config ./custom_config.yaml --log-level DEBUG

# Run with SSE transport for web applications
uv run python -m mcp_ai_hub.server --transport sse --port 3001

# Run with HTTP transport
uv run python -m mcp_ai_hub.server --transport http --port 8080
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage reporting
uv run pytest --cov=src/mcp_ai_hub --cov-report=html

# Run specific test file
uv run pytest tests/test_ai_client.py

# Run with debug output
uv run pytest -v -s
```

### Code Quality
```bash
# Format code with ruff
uv run ruff format .

# Lint code
uv run ruff check .

# Fix linting issues automatically
uv run ruff check . --fix

# Type checking with mypy
uv run mypy src/

# Run all quality checks
uv run ruff format . && uv run ruff check . && uv run mypy src/
```

## Key Components

### AIHubConfig (config.py)
- Pydantic models for YAML configuration validation
- Loads from `~/.ai_hub.yaml` by default
- Validates model configurations and LiteLM parameters

### AIClient (ai_client.py)
- Wrapper around LiteLM for unified AI provider access
- Handles message format conversion (string → OpenAI format)
- Error handling and response parsing
- Supports both string and OpenAI-style message inputs

### FastMCP Server (server.py)
- Implements MCP protocol using FastMCP framework
- Provides three main tools: `chat()`, `list_models()`, `get_model_info()`
- Supports multiple transports: stdio, SSE, HTTP
- Global AI client initialization and management

## Configuration

The server expects configuration at `~/.ai_hub.yaml` with this structure:

```yaml
model_list:
  - model_name: gpt-4  # Friendly name for MCP tools
    litellm_params:
      model: openai/gpt-4  # LiteLM provider/model format
      api_key: "sk-your-key"
      max_tokens: 2048
      temperature: 0.7

  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20241022
      api_key: "sk-ant-your-key"
      max_tokens: 4096
```

See `config_example.yaml` for comprehensive configuration examples.

## MCP Tools

The server exposes these tools to MCP clients:

### chat(model: str, messages: list[dict]) → dict
- Send messages to any configured AI model using OpenAI-compatible format
- Accepts OpenAI-format message lists with support for multimodal content
- Returns complete LiteLM ModelResponse as dictionary

**Message Format:**
- Each message must have 'role' and 'content' keys
- Content can be a string for text or a list for multimodal (text, images, etc.)

**⚠️ IMPORTANT: Local Image Handling**
- For local images, simply use the absolute file path as the URL
- The server will automatically detect local paths and convert them to base64
- This prevents token limit issues by handling the conversion server-side

**Supported Image Formats:**
- **Remote URL**: `"url": "https://example.com/image.jpg"`
- **Local file path**: `"url": "/path/to/local/image.jpg"` (auto-converted to base64)
- **Base64**: `"url": "data:image/jpeg;base64,<base64_string>"`

**Examples:**
```python
# Simple text message
messages = [{"role": "user", "content": "Hello!"}]

# Multiple messages (conversation)
messages = [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "user", "content": "How are you?"}
]

# Multimodal message with remote image URL
messages = [{
    "role": "user",
    "content": [
        {"type": "text", "text": "What's in this image?"},
        {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
    ]
}]

# Multimodal message with local image (absolute path)
# The server will automatically convert local paths to base64
messages = [{
    "role": "user",
    "content": [
        {"type": "text", "text": "What's in this image?"},
        {"type": "image_url", "image_url": {"url": "/Users/john/Desktop/screenshot.png"}}
    ]
}]

# Windows path example
messages = [{
    "role": "user",
    "content": [
        {"type": "text", "text": "Analyze this photo"},
        {"type": "image_url", "image_url": {"url": "C:\\Users\\john\\Pictures\\photo.jpg"}}
    ]
}]
```

**Response Format:**
Returns complete LiteLM ModelResponse containing:
- `id`: Response ID
- `object`: Response object type ('chat.completion')
- `created`: Timestamp
- `model`: Model used
- `choices`: List of completion choices with message content
- `usage`: Token usage statistics (prompt_tokens, completion_tokens, total_tokens)

### list_models() → list[str]
- Returns list of all configured model names

### get_model_info(model: str) → dict
- Returns configuration details for specific model
- Includes provider, model identifier, and configured parameters

## Testing Architecture

- **conftest.py**: Shared test fixtures and mock configurations
- **test_config.py**: Configuration loading and validation tests
- **test_ai_client.py**: AIClient functionality and LiteLM integration tests
- **test_server.py**: FastMCP server and tool integration tests

Tests use pytest with async support and comprehensive mocking of external dependencies.

## Dependencies

### Runtime Dependencies
- **mcp**: FastMCP server framework for MCP protocol
- **litellm**: Unified API for 100+ AI providers
- **httpx[socks]**: HTTP client with proxy support
- **pyyaml**: YAML configuration parsing
- **pydantic**: Configuration validation and serialization

### Development Dependencies
- **pytest** + **pytest-asyncio** + **pytest-cov**: Testing framework
- **ruff**: Fast linting and formatting
- **mypy**: Static type checking
- **pre-commit**: Git hooks for code quality

## Code Conventions

- **Type Hints**: All functions use comprehensive type annotations
- **Error Handling**: Robust exception handling with informative messages
- **Logging**: Uses Python logging with stderr output (MCP requirement)
- **Async**: Proper async/await patterns for MCP server operations
- **Configuration**: Pydantic models for type-safe configuration
- **Testing**: High test coverage with mocked external dependencies

## Transport Types

- **stdio**: Standard input/output (default for MCP clients like Claude Desktop/Code)
- **sse**: Server-Sent Events for web applications
- **http**: HTTP transport with streaming support for direct API calls

Each transport is configured via CLI arguments (`--transport`, `--host`, `--port`).