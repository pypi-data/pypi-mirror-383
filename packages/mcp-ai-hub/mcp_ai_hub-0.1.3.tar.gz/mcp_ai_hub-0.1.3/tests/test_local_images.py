"""Tests for local image handling functionality."""

import base64
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mcp_ai_hub.ai_client import AIClient
from mcp_ai_hub.config import AIHubConfig, ModelConfig


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock(spec=AIHubConfig)
    config.model_list = [
        ModelConfig(
            model_name="test-model",
            litellm_params={"model": "openai/gpt-4-vision-preview"},
        )
    ]
    config.global_system_prompt = None
    config.list_available_models.return_value = ["test-model"]
    config.get_model_config.return_value = config.model_list[0]
    return config


@pytest.fixture
def ai_client(mock_config):
    """Create an AI client with mock configuration."""
    return AIClient(mock_config)


def test_is_local_path(ai_client):
    """Test local path detection."""
    # Local paths - should return True
    assert ai_client._is_local_path("/path/to/image.jpg") is True
    assert ai_client._is_local_path("/Users/john/Desktop/photo.png") is True
    assert ai_client._is_local_path("C:\\Users\\john\\Pictures\\image.jpg") is True
    assert ai_client._is_local_path("D:\\photos\\vacation.png") is True

    # Non-local paths - should return False
    assert ai_client._is_local_path("https://example.com/image.jpg") is False
    assert ai_client._is_local_path("http://example.com/image.jpg") is False
    assert ai_client._is_local_path("data:image/jpeg;base64,abc123") is False
    assert ai_client._is_local_path("relative/path/image.jpg") is False


def test_read_and_encode_image(ai_client):
    """Test reading and encoding a local image file."""
    # Create a temporary image file
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
        # Write some dummy image data
        test_data = b"fake image data"
        tmp_file.write(test_data)
        tmp_file_path = tmp_file.name

    try:
        # Test successful encoding
        result = ai_client._read_and_encode_image(tmp_file_path)
        assert result is not None
        assert result.startswith("data:image/jpeg;base64,")

        # Decode and verify the data
        base64_part = result.split(",")[1]
        decoded_data = base64.b64decode(base64_part)
        assert decoded_data == test_data

        # Test non-existent file
        result = ai_client._read_and_encode_image("/non/existent/file.jpg")
        assert result is None

    finally:
        # Clean up
        Path(tmp_file_path).unlink()


def test_process_content_item(ai_client):
    """Test processing individual content items."""
    # Create a temporary image file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        tmp_file.write(b"test image")
        tmp_file_path = tmp_file.name

    try:
        # Test local image path conversion
        item = {"type": "image_url", "image_url": {"url": tmp_file_path}}
        processed = ai_client._process_content_item(item)
        assert processed["image_url"]["url"].startswith("data:image/png;base64,")

        # Test remote URL (should not be modified)
        item = {
            "type": "image_url",
            "image_url": {"url": "https://example.com/image.jpg"},
        }
        processed = ai_client._process_content_item(item)
        assert processed["image_url"]["url"] == "https://example.com/image.jpg"

        # Test text content (should not be modified)
        item = {"type": "text", "text": "Hello"}
        processed = ai_client._process_content_item(item)
        assert processed == item

        # Test non-dict item
        processed = ai_client._process_content_item("plain string")
        assert processed == "plain string"

    finally:
        Path(tmp_file_path).unlink()


def test_process_messages_for_local_images(ai_client):
    """Test processing messages with local images."""
    # Create temporary image files
    with (
        tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp1,
        tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp2,
    ):
        tmp1.write(b"image 1")
        tmp2.write(b"image 2")
        path1, path2 = tmp1.name, tmp2.name

    try:
        # Test message with multiple local images
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Look at these images"},
                    {"type": "image_url", "image_url": {"url": path1}},
                    {"type": "image_url", "image_url": {"url": path2}},
                ],
            },
            {"role": "assistant", "content": "I'll analyze them"},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "And this one"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://example.com/remote.jpg"},
                    },
                ],
            },
        ]

        processed = ai_client._process_messages_for_local_images(messages)

        # Check first message - local images should be converted
        assert processed[0]["content"][0]["type"] == "text"
        assert processed[0]["content"][1]["image_url"]["url"].startswith(
            "data:image/jpeg;base64,"
        )
        assert processed[0]["content"][2]["image_url"]["url"].startswith(
            "data:image/png;base64,"
        )

        # Check second message - string content should be unchanged
        assert processed[1]["content"] == "I'll analyze them"

        # Check third message - remote URL should be unchanged
        assert processed[2]["content"][0]["type"] == "text"
        assert (
            processed[2]["content"][1]["image_url"]["url"]
            == "https://example.com/remote.jpg"
        )

    finally:
        Path(path1).unlink()
        Path(path2).unlink()


def test_chat_with_local_images(ai_client, mock_config):
    """Test the chat method with local images."""
    # Create a temporary image file
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
        tmp_file.write(b"test image data")
        tmp_file_path = tmp_file.name

    try:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {"type": "image_url", "image_url": {"url": tmp_file_path}},
                ],
            }
        ]

        # Mock the litellm.completion call
        with patch("mcp_ai_hub.ai_client.litellm.completion") as mock_completion:
            mock_response = MagicMock()
            mock_response.model_dump.return_value = {
                "choices": [{"message": {"content": "I see an image"}}]
            }
            mock_completion.return_value = mock_response

            # Call chat method
            ai_client.chat("test-model", messages)

            # Verify that litellm was called with base64-encoded image
            called_messages = mock_completion.call_args[1]["messages"]
            assert len(called_messages) == 1
            assert called_messages[0]["content"][1]["image_url"]["url"].startswith(
                "data:image/jpeg;base64,"
            )

    finally:
        Path(tmp_file_path).unlink()


def test_mixed_image_types(ai_client):
    """Test handling of mixed image types in a single message."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
        tmp_file.write(b"local image")
        local_path = tmp_file.name

    try:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Compare these images"},
                    {"type": "image_url", "image_url": {"url": local_path}},
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://example.com/remote.jpg"},
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/png;base64,iVBORw0KGgo="},
                    },
                ],
            }
        ]

        processed = ai_client._process_messages_for_local_images(messages)

        # Local path should be converted
        assert processed[0]["content"][1]["image_url"]["url"].startswith(
            "data:image/jpeg;base64,"
        )
        # Remote URL should remain unchanged
        assert (
            processed[0]["content"][2]["image_url"]["url"]
            == "https://example.com/remote.jpg"
        )
        # Base64 should remain unchanged
        assert (
            processed[0]["content"][3]["image_url"]["url"]
            == "data:image/png;base64,iVBORw0KGgo="
        )

    finally:
        Path(local_path).unlink()
