"""Configuration management for MCP AI Hub."""

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ModelConfig(BaseModel):
    """Configuration for a single AI model."""

    model_name: str
    litellm_params: dict[str, Any]
    system_prompt: str | None = None  # Optional system prompt for this model


class AIHubConfig(BaseModel):
    """Main configuration for AI Hub."""

    model_list: list[ModelConfig] = Field(default_factory=list)
    global_system_prompt: str | None = (
        None  # Optional global system prompt for all models
    )

    @classmethod
    def get_default_config_path(cls) -> Path:
        """Get the default configuration file path."""
        return Path.home() / ".ai_hub.yaml"

    @classmethod
    def load_config(cls, config_path: Path | None = None) -> "AIHubConfig":
        """Load configuration from file."""
        if config_path is None:
            config_path = cls.get_default_config_path()

        if not config_path.exists():
            logger.warning(
                f"Configuration file not found at {config_path}, using empty config"
            )
            return cls()

        try:
            with open(config_path) as f:
                config_data = yaml.safe_load(f)

            return cls(**config_data)
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            raise

    def get_model_config(self, model_name: str) -> ModelConfig | None:
        """Get configuration for a specific model."""
        for model in self.model_list:
            if model.model_name == model_name:
                return model
        return None

    def list_available_models(self) -> list[str]:
        """List all available model names."""
        return [model.model_name for model in self.model_list]
