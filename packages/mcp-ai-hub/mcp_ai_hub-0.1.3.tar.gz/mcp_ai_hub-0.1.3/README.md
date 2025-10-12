# MCP AI Hub

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/) [![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![PyPI Downloads](https://static.pepy.tech/badge/mcp-ai-hub)](https://pepy.tech/projects/mcp-ai-hub)

A Model Context Protocol (MCP) server that provides unified access to various AI providers through LiteLM. Chat with OpenAI, Anthropic, and 100+ other AI models using a single, consistent interface.

## 🌟 Overview

MCP AI Hub acts as a bridge between MCP clients (like Claude Desktop/Code) and multiple AI providers. It leverages LiteLM's unified API to provide seamless access to 100+ AI models without requiring separate integrations for each provider.

**Key Benefits:**

- **Unified Interface**: Single API for all AI providers
- **100+ Providers**: OpenAI, Anthropic, Google, Azure, AWS Bedrock, and more
- **MCP Protocol**: Native integration with Claude Desktop and Claude Code
- **Flexible Configuration**: YAML-based configuration with Pydantic validation
- **Multiple Transports**: stdio, SSE, and HTTP transport options
- **Custom Endpoints**: Support for proxy servers and local deployments

## Quick Start

### 1. Install

Choose your preferred installation method:

```bash
# Option A: Install from PyPI
pip install mcp-ai-hub

# Option B: Install with uv (recommended)
uv tool install mcp-ai-hub

# Option C: Install from source
pip install git+https://github.com/your-username/mcp-ai-hub.git
```

**Installation Notes:**

- `uv` is a fast Python package installer and resolver
- The package requires Python 3.10 or higher
- All dependencies are automatically resolved and installed

### 2. Configure

Create a configuration file at `~/.ai_hub.yaml` with your API keys and model configurations:

```yaml
model_list:
  - model_name: gpt-4  # Friendly name you'll use in MCP tools
    litellm_params:
      model: openai/gpt-4  # LiteLM provider/model identifier
      api_key: "sk-your-openai-api-key-here"  # Your actual OpenAI API key
      max_tokens: 2048  # Maximum response tokens
      temperature: 0.7  # Response creativity (0.0-1.0)

  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20241022
      api_key: "sk-ant-your-anthropic-api-key-here"
      max_tokens: 4096
      temperature: 0.7
```

**Configuration Guidelines:**

- **API Keys**: Replace placeholder keys with your actual API keys
- **Model Names**: Use descriptive names you'll remember (e.g., `gpt-4`, `claude-sonnet`)
- **LiteLM Models**: Use LiteLM's provider/model format (e.g., `openai/gpt-4`, `anthropic/claude-3-5-sonnet-20241022`)
- **Parameters**: Configure `max_tokens`, `temperature`, and other LiteLM-supported parameters
- **Security**: Keep your config file secure with appropriate file permissions (chmod 600)

### 3. Connect to Claude Desktop

Configure Claude Desktop to use MCP AI Hub by editing your configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ai-hub": {
      "command": "mcp-ai-hub"
    }
  }
}
```

### 4. Connect to Claude Code

```sh
claude mcp add -s user ai-hub mcp-ai-hub
```

## Advanced Usage

### CLI Options and Transport Types

MCP AI Hub supports multiple transport mechanisms for different use cases:

**Command Line Options:**

```bash
# Default stdio transport (for MCP clients like Claude Desktop)
mcp-ai-hub

# Server-Sent Events transport (for web applications)
mcp-ai-hub --transport sse --host 0.0.0.0 --port 3001

# Streamable HTTP transport (for direct API calls)
mcp-ai-hub --transport http --port 8080

# Custom config file and debug logging
mcp-ai-hub --config /path/to/config.yaml --log-level DEBUG
```

**Transport Type Details:**

| Transport | Use Case | Default Host:Port | Description |
|-----------|----------|-------------------|-------------|
| `stdio` | MCP clients (Claude Desktop/Code) | N/A | Standard input/output, default for MCP |
| `sse` | Web applications | localhost:3001 | Server-Sent Events for real-time web apps |
| `http` | Direct API calls | localhost:3001 (override with `--port`) | HTTP transport with streaming support |

**CLI Arguments:**

- `--transport {stdio,sse,http}`: Transport protocol (default: stdio)
- `--host HOST`: Host address for SSE/HTTP (default: localhost)
- `--port PORT`: Port number for SSE/HTTP (default: 3001; override if you need a different port)
- `--config CONFIG`: Custom config file path (default: ~/.ai_hub.yaml)
- `--log-level {DEBUG,INFO,WARNING,ERROR}`: Logging verbosity (default: INFO)

## Usage

Once MCP AI Hub is connected to your MCP client, you can interact with AI models using these tools:

### MCP Tool Reference

**Primary Chat Tool:**

```python
chat(model_name: str, message: str | list[dict]) -> str
```

- **model_name**: Name of the configured model (e.g., "gpt-4", "claude-sonnet")
- **message**: String message or OpenAI-style message list
- **Returns**: AI model response as string

**Model Discovery Tools:**

```python
list_models() -> list[str]
```

- **Returns**: List of all configured model names

```python
get_model_info(model_name: str) -> dict
```

- **model_name**: Name of the configured model
- **Returns**: Model configuration details including provider, parameters, etc.

## Configuration

MCP AI Hub supports 100+ AI providers through LiteLM. Configure your models in `~/.ai_hub.yaml` with API keys and custom parameters.

### System Prompts

You can define system prompts at two levels:

- `global_system_prompt`: Applied to all models by default
- Per-model `system_prompt`: Overrides the global prompt for that model

Precedence: model-specific prompt > global prompt. If a model's `system_prompt` is set to an empty string, it disables the global prompt for that model.

```yaml
global_system_prompt: "You are a helpful AI assistant. Be concise."

model_list:
  - model_name: gpt-4
    system_prompt: "You are a precise coding assistant."
    litellm_params:
      model: openai/gpt-4
      api_key: "sk-your-openai-api-key"

  - model_name: claude-sonnet
    # Empty string disables the global prompt for this model
    system_prompt: ""
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20241022
      api_key: "sk-ant-your-anthropic-api-key"
```

Notes:
- The server prepends the configured system prompt to the message list it sends to providers.
- If you pass an explicit message list that already contains a `system` message, both system messages will be included in order (configured prompt first).

### Supported Providers

**Major AI Providers:**

- **OpenAI**: GPT-4, GPT-3.5-turbo, GPT-4-turbo, etc.
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Haiku, Claude 3 Opus
- **Google**: Gemini Pro, Gemini Pro Vision, Gemini Ultra
- **Azure OpenAI**: Azure-hosted OpenAI models
- **AWS Bedrock**: Claude, Llama, Jurassic, and more
- **Together AI**: Llama, Mistral, Falcon, and open-source models
- **Hugging Face**: Various open-source models
- **Local Models**: Ollama, LM Studio, and other local deployments

**Configuration Parameters:**

- **api_key**: Your provider API key (required)
- **max_tokens**: Maximum response tokens (optional)
- **temperature**: Response creativity 0.0-1.0 (optional)
- **api_base**: Custom endpoint URL (for proxies/local servers)
- **Additional**: All LiteLM-supported parameters

### Configuration Examples

**Basic Configuration:**

```yaml
global_system_prompt: "You are a helpful AI assistant. Be concise."

model_list:
  - model_name: gpt-4
    system_prompt: "You are a precise coding assistant."  # overrides global
    litellm_params:
      model: openai/gpt-4
      api_key: "sk-your-actual-openai-api-key"
      max_tokens: 2048
      temperature: 0.7

  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20241022
      api_key: "sk-ant-your-actual-anthropic-api-key"
      max_tokens: 4096
      temperature: 0.7
```

**Custom Parameters:**

```yaml
model_list:
  - model_name: gpt-4-creative
    litellm_params:
      model: openai/gpt-4
      api_key: "sk-your-openai-key"
      max_tokens: 4096
      temperature: 0.9  # Higher creativity
      top_p: 0.95
      frequency_penalty: 0.1
      presence_penalty: 0.1

  - model_name: claude-analytical
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20241022
      api_key: "sk-ant-your-anthropic-key"
      max_tokens: 8192
      temperature: 0.3  # Lower creativity for analytical tasks
      stop_sequences: ["\n\n", "Human:"]
```

**Local LLM Server Configuration:**

```yaml
model_list:
  - model_name: local-llama
    litellm_params:
      model: openai/llama-2-7b-chat
      api_key: "dummy-key"  # Local servers often accept any API key
      api_base: "http://localhost:8080/v1"  # Local OpenAI-compatible server
      max_tokens: 2048
      temperature: 0.7
```

For more providers, please refer to the LiteLLM docs: <https://docs.litellm.ai/docs/providers>.

## Development

**Setup:**

```bash
# Install all dependencies including dev dependencies
uv sync

# Install package in development mode
uv pip install -e ".[dev]"

# Add new runtime dependencies
uv add package_name

# Add new development dependencies
uv add --dev package_name

# Update dependencies
uv sync --upgrade
```

**Running and Testing:**

```bash
# Run the MCP server
uv run mcp-ai-hub

# Run with custom configuration
uv run mcp-ai-hub --config ./custom_config.yaml --log-level DEBUG

# Run with different transport
uv run mcp-ai-hub --transport sse --port 3001

# Run tests (when test suite is added)
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/mcp_ai_hub --cov-report=html
```

**Code Quality:**

```bash
# Format code with ruff
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking with mypy
uv run mypy src/

# Run all quality checks
uv run ruff format . && uv run ruff check . && uv run mypy src/
```

## Troubleshooting

### Configuration Issues

**Configuration File Problems:**

- **File Location**: Ensure `~/.ai_hub.yaml` exists in your home directory
- **YAML Validity**: Validate YAML syntax using online validators or `python -c "import yaml; yaml.safe_load(open('~/.ai_hub.yaml'))"`
- **File Permissions**: Set secure permissions with `chmod 600 ~/.ai_hub.yaml`
- **Path Resolution**: Use absolute paths in custom config locations

**Configuration Validation:**

- **Required Fields**: Each model must have `model_name` and `litellm_params`
- **API Keys**: Verify API keys are properly quoted and not expired
- **Model Formats**: Use LiteLM-compatible model identifiers (e.g., `openai/gpt-4`, `anthropic/claude-3-5-sonnet-20241022`)

### API and Authentication Errors

**Authentication Issues:**

- **Invalid API Keys**: Check for typos, extra spaces, or expired keys
- **Insufficient Permissions**: Verify API keys have necessary model access permissions
- **Rate Limiting**: Monitor API usage and implement retry logic if needed
- **Regional Restrictions**: Some models may not be available in all regions

**API-Specific Troubleshooting:**

- **OpenAI**: Check organization settings and model availability
- **Anthropic**: Verify Claude model access and usage limits
- **Azure OpenAI**: Ensure proper resource deployment and endpoint configuration
- **Google Gemini**: Check project setup and API enablement

### MCP Connection Issues

**Server Startup Problems:**

- **Port Conflicts**: Use different ports for SSE/HTTP transports if defaults are in use
- **Permission Errors**: Ensure executable permissions for `mcp-ai-hub` command
- **Python Path**: Verify Python environment and package installation

**Client Configuration Issues:**

- **Command Path**: Ensure `mcp-ai-hub` is in PATH or use full absolute path
- **Working Directory**: Some MCP clients require specific working directory settings
- **Transport Mismatch**: Use stdio transport for Claude Desktop/Code

### Performance and Reliability

**Response Time Issues:**

- **Network Latency**: Use geographically closer API endpoints when possible
- **Model Selection**: Some models are faster than others (e.g., GPT-3.5 vs GPT-4)
- **Token Limits**: Large `max_tokens` values can increase response time

**Reliability Improvements:**

- **Retry Logic**: Implement exponential backoff for transient failures
- **Timeout Configuration**: Set appropriate timeouts for your use case
- **Health Checks**: Monitor server status and restart if needed
- **Load Balancing**: Use multiple model configurations for redundancy

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please follow these guidelines:

### Development Workflow

1. **Fork and Clone**: Fork the repository and clone your fork
2. **Create Branch**: Create a feature branch (`git checkout -b feature/amazing-feature`)
3. **Development Setup**: Install dependencies with `uv sync`
4. **Make Changes**: Implement your feature or fix
5. **Testing**: Add tests and ensure all tests pass
6. **Code Quality**: Run formatting, linting, and type checking
7. **Documentation**: Update documentation if needed
8. **Submit PR**: Create a pull request with detailed description

### Code Standards

**Python Style:**

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Add docstrings for public functions and classes
- Keep functions focused and small

**Testing Requirements:**

- Write tests for new functionality
- Ensure existing tests continue to pass
- Aim for good test coverage
- Test edge cases and error conditions

**Documentation:**

- Update README.md for user-facing changes
- Add inline comments for complex logic
- Update configuration examples if needed
- Document breaking changes clearly

### Quality Checks

Before submitting a PR, ensure:

```bash
# All tests pass
uv run pytest

# Code formatting
uv run ruff format .

# Linting passes
uv run ruff check .

# Type checking passes
uv run mypy src/

# Documentation is up to date
# Configuration examples are valid
```

### Issues and Feature Requests

- Use GitHub Issues for bug reports and feature requests
- Provide detailed reproduction steps for bugs
- Include configuration examples when relevant
- Check existing issues before creating new ones
- Label issues appropriately
