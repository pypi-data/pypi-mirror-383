"""Unit tests for configuration management."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from mcp_ai_hub.config import AIHubConfig, ModelConfig


class TestModelConfig:
    """Test ModelConfig class."""

    def test_model_config_creation(self):
        """Test creating a ModelConfig instance."""
        config = ModelConfig(
            model_name="gpt-4",
            litellm_params={"model": "openai/gpt-4", "api_key": "test-key"},
        )
        assert config.model_name == "gpt-4"
        assert config.litellm_params["model"] == "openai/gpt-4"
        assert config.litellm_params["api_key"] == "test-key"
        assert config.system_prompt is None

    def test_model_config_with_system_prompt(self):
        """Test creating a ModelConfig with system prompt."""
        config = ModelConfig(
            model_name="gpt-4",
            litellm_params={"model": "openai/gpt-4", "api_key": "test-key"},
            system_prompt="You are a helpful assistant.",
        )
        assert config.model_name == "gpt-4"
        assert config.system_prompt == "You are a helpful assistant."

    def test_model_config_validation(self):
        """Test ModelConfig validation."""
        # Missing required field
        with pytest.raises(ValueError):
            ModelConfig(litellm_params={"model": "openai/gpt-4"})  # type: ignore

        with pytest.raises(ValueError):
            ModelConfig(model_name="gpt-4")  # type: ignore


class TestAIHubConfig:
    """Test AIHubConfig class."""

    def test_default_config_path(self):
        """Test getting default config path."""
        path = AIHubConfig.get_default_config_path()
        assert path == Path.home() / ".ai_hub.yaml"

    def test_empty_config(self):
        """Test creating empty config."""
        config = AIHubConfig()
        assert config.model_list == []
        assert config.global_system_prompt is None

    def test_config_with_global_system_prompt(self):
        """Test creating config with global system prompt."""
        config = AIHubConfig(global_system_prompt="Global system prompt")
        assert config.global_system_prompt == "Global system prompt"

    def test_config_with_models(self):
        """Test creating config with models."""
        model_configs = [
            ModelConfig(
                model_name="gpt-4",
                litellm_params={"model": "openai/gpt-4", "api_key": "test-key"},
            ),
            ModelConfig(
                model_name="claude-sonnet",
                litellm_params={
                    "model": "anthropic/claude-3-sonnet",
                    "api_key": "test-key",
                },
            ),
        ]
        config = AIHubConfig(model_list=model_configs)
        assert len(config.model_list) == 2
        assert config.model_list[0].model_name == "gpt-4"
        assert config.model_list[1].model_name == "claude-sonnet"

    def test_get_model_config_existing(self):
        """Test getting model config for existing model."""
        model_configs = [
            ModelConfig(
                model_name="gpt-4",
                litellm_params={"model": "openai/gpt-4", "api_key": "test-key"},
            )
        ]
        config = AIHubConfig(model_list=model_configs)

        model_config = config.get_model_config("gpt-4")
        assert model_config is not None
        assert model_config.model_name == "gpt-4"
        assert model_config.litellm_params["model"] == "openai/gpt-4"

    def test_get_model_config_non_existing(self):
        """Test getting model config for non-existing model."""
        config = AIHubConfig()
        model_config = config.get_model_config("non-existing")
        assert model_config is None

    def test_list_available_models(self):
        """Test listing available models."""
        model_configs = [
            ModelConfig(
                model_name="gpt-4",
                litellm_params={"model": "openai/gpt-4", "api_key": "test-key"},
            ),
            ModelConfig(
                model_name="claude-sonnet",
                litellm_params={
                    "model": "anthropic/claude-3-sonnet",
                    "api_key": "test-key",
                },
            ),
        ]
        config = AIHubConfig(model_list=model_configs)

        models = config.list_available_models()
        assert len(models) == 2
        assert "gpt-4" in models
        assert "claude-sonnet" in models


class TestAIHubConfigLoading:
    """Test configuration loading functionality."""

    def test_load_config_non_existing_file(self):
        """Test loading config from non-existing file."""
        with patch("mcp_ai_hub.config.logger") as mock_logger:
            config = AIHubConfig.load_config(Path("/non/existing/path.yaml"))
            assert isinstance(config, AIHubConfig)
            assert config.model_list == []
            mock_logger.warning.assert_called_once()

    def test_load_config_valid_file(self):
        """Test loading config from valid YAML file."""
        config_data = {
            "model_list": [
                {
                    "model_name": "gpt-4",
                    "litellm_params": {"model": "openai/gpt-4", "api_key": "test-key"},
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = Path(f.name)

        try:
            config = AIHubConfig.load_config(temp_path)
            assert len(config.model_list) == 1
            assert config.model_list[0].model_name == "gpt-4"
            assert config.model_list[0].litellm_params["model"] == "openai/gpt-4"
        finally:
            temp_path.unlink()

    def test_load_config_with_system_prompts(self):
        """Test loading config with system prompts."""
        config_data = {
            "global_system_prompt": "Global system prompt",
            "model_list": [
                {
                    "model_name": "gpt-4",
                    "system_prompt": "Model-specific system prompt",
                    "litellm_params": {"model": "openai/gpt-4", "api_key": "test-key"},
                },
                {
                    "model_name": "claude-sonnet",
                    "litellm_params": {
                        "model": "anthropic/claude-sonnet",
                        "api_key": "test-key",
                    },
                },
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = Path(f.name)

        try:
            config = AIHubConfig.load_config(temp_path)
            assert config.global_system_prompt == "Global system prompt"
            assert len(config.model_list) == 2
            assert config.model_list[0].model_name == "gpt-4"
            assert config.model_list[0].system_prompt == "Model-specific system prompt"
            assert config.model_list[1].model_name == "claude-sonnet"
            assert config.model_list[1].system_prompt is None
        finally:
            temp_path.unlink()

    def test_load_config_invalid_yaml(self):
        """Test loading config from invalid YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_path = Path(f.name)

        try:
            with pytest.raises(yaml.scanner.ScannerError):
                AIHubConfig.load_config(temp_path)
        finally:
            temp_path.unlink()
