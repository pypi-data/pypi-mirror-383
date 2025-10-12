"""Test configuration and fixtures."""

import tempfile
from pathlib import Path
from typing import Any

import pytest
import yaml

from mcp_ai_hub.config import AIHubConfig, ModelConfig


def create_test_config(models: list[dict[str, Any]]) -> AIHubConfig:
    """Create a test configuration with the specified models."""
    model_configs = []
    for model_data in models:
        model_config = ModelConfig(
            model_name=model_data["model_name"],
            litellm_params=model_data["litellm_params"],
        )
        model_configs.append(model_config)

    return AIHubConfig(model_list=model_configs)


def create_temp_config_file(config_data: dict[str, Any]) -> Path:
    """Create a temporary YAML config file with the given data."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        return Path(f.name)


@pytest.fixture
def sample_config_data() -> dict[str, Any]:
    """Sample configuration data for testing."""
    return {
        "model_list": [
            {
                "model_name": "gpt-4",
                "litellm_params": {
                    "model": "openai/gpt-4",
                    "api_key": "${OPENAI_API_KEY}",
                    "max_tokens": 2048,
                    "temperature": 0.7,
                },
            },
            {
                "model_name": "claude-sonnet",
                "litellm_params": {
                    "model": "anthropic/claude-3-5-sonnet-20241022",
                    "api_key": "${ANTHROPIC_API_KEY}",
                },
            },
        ]
    }


@pytest.fixture
def sample_config(sample_config_data: dict[str, Any]) -> AIHubConfig:
    """Sample configuration for testing."""
    return create_test_config(sample_config_data["model_list"])


@pytest.fixture
def temp_config_file(sample_config_data: dict[str, Any]) -> Path:
    """Temporary config file fixture."""
    temp_path = create_temp_config_file(sample_config_data)
    yield temp_path
    temp_path.unlink()


@pytest.fixture
def mock_litellm_response():
    """Mock LiteLM response object."""

    class MockMessage:
        def __init__(self, content: str):
            self.content = content

    class MockChoice:
        def __init__(self, message: MockMessage):
            self.message = message

    class MockResponse:
        def __init__(self, content: str):
            self.choices = [MockChoice(MockMessage(content))]

    return MockResponse


@pytest.fixture
def mock_litellm_empty_response():
    """Mock LiteLM empty response object."""

    class MockResponse:
        def __init__(self):
            self.choices = []

    return MockResponse


@pytest.fixture
def mock_litellm_no_content_response():
    """Mock LiteLM response with no content."""

    class MockMessage:
        def __init__(self):
            self.content = None

    class MockChoice:
        def __init__(self, message: MockMessage):
            self.message = message

    class MockResponse:
        def __init__(self):
            self.choices = [MockChoice(MockMessage())]

    return MockResponse
