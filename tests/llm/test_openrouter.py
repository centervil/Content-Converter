"""Tests for the OpenRouterProvider class."""
import os
import pytest
import json
from unittest.mock import MagicMock, patch, ANY
import requests
from requests.exceptions import HTTPError

from content_converter.llm.openrouter import OpenRouterProvider


class TestOpenRouterProvider:
    """Test suite for OpenRouterProvider."""

    @patch('requests.post')
    def test_init_with_env_var(self, mock_post, monkeypatch):
        """Test initialization with API key from environment variable."""
        # Arrange
        monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "test response"}}]}
        mock_post.return_value = mock_response

        # Act
        provider = OpenRouterProvider()

        # Assert
        assert provider.api_key == "test_api_key"
        assert provider.model == "anthropic/claude-3-opus-20240229"
        assert provider.headers["Authorization"] == "Bearer test_api_key"
        assert provider.headers["HTTP-Referer"] == "https://github.com/centervil/Content-Converter"
        assert provider.headers["X-Title"] == "Content Converter"

    @patch('requests.post')
    def test_init_with_api_key_param(self, mock_post):
        """Test initialization with API key passed as parameter."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "test response"}}]}
        mock_post.return_value = mock_response

        # Act
        provider = OpenRouterProvider(api_key="direct_key", model="custom/model")

        # Assert
        assert provider.api_key == "direct_key"
        assert provider.model == "custom/model"
        assert provider.headers["Authorization"] == "Bearer direct_key"
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises ValueError."""
        # Arrange & Act & Assert
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OpenRouter APIキーが設定されていません"):
                OpenRouterProvider()

    @patch('requests.post')
    def test_optimize_content(self, mock_post):
        """Test content optimization with default options."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "Optimized content"}}]}
        mock_post.return_value = mock_response
        
        provider = OpenRouterProvider(api_key="test_key")
        
        # Act
        result = provider.optimize_content("Test content")
        
        # Assert
        assert result == "Optimized content"
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://openrouter.ai/api/v1/chat/completions"
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_key"
        
        request_data = call_args[1]["json"]
        assert request_data["model"] == "anthropic/claude-3-opus-20240229"
        assert request_data["temperature"] == 0.7
        assert request_data["max_tokens"] == 2048
        assert "Test content" in request_data["messages"][0]["content"]
        
    @patch('requests.post')
    def test_optimize_content_with_custom_options(self, mock_post):
        """Test content optimization with custom options."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "Custom optimized content"}}]}
        mock_post.return_value = mock_response
        
        provider = OpenRouterProvider(api_key="test_key")
        
        # Act
        result = provider.optimize_content(
            "Test content",
            options={
                "model": "custom/model",
                "temperature": 0.9,
                "max_tokens": 1000
            }
        )
        
        # Assert
        assert result == "Custom optimized content"
        request_data = mock_post.call_args[1]["json"]
        assert request_data["model"] == "custom/model"
        assert request_data["temperature"] == 0.9
        assert request_data["max_tokens"] == 1000

    @patch('requests.post')
    def test_generate_summary(self, mock_post):
        """Test summary generation."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "This is a summary."}}]}
        mock_post.return_value = mock_response
        
        provider = OpenRouterProvider(api_key="test_key")
        
        # Act
        result = provider.generate_summary("Long content " * 100, max_length=50)
        
        # Assert
        assert result == "This is a summary."
        request_data = mock_post.call_args[1]["json"]
        assert "Long content" in request_data["messages"][0]["content"]
        assert "50文字以内" in request_data["messages"][0]["content"]

    @patch('requests.post')
    def test_optimize_content_http_error(self, mock_post):
        """Test handling of HTTP errors during content optimization."""
        # Arrange
        mock_response = MagicMock()
        http_error = HTTPError("API error")
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response
        
        provider = OpenRouterProvider(api_key="test_key")
        
        # Act & Assert
        with pytest.raises(HTTPError, match="API error"):
            provider.optimize_content("Test content")

    @patch('requests.post')
    def test_optimize_content_invalid_response(self, mock_post):
        """Test handling of invalid API response."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "response"}  # Missing expected fields
        mock_post.return_value = mock_response
        
        provider = OpenRouterProvider(api_key="test_key")
        
        # Act & Assert
        with pytest.raises(KeyError):
            provider.optimize_content("Test content")
