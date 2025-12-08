"""Tests for the GeminiProvider class."""
import os
import pytest
from unittest.mock import MagicMock, patch, ANY
from google.api_core import exceptions as google_exceptions

from content_converter.llm.gemini import GeminiProvider


class TestGeminiProvider:
    """Test suite for GeminiProvider."""

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_init_with_env_var(self, mock_gen_model, mock_configure, monkeypatch):
        """Test initialization with API key from environment variable."""
        # Arrange
        monkeypatch.setenv("GOOGLE_API_KEY", "test_api_key")
        mock_model = MagicMock()
        mock_gen_model.return_value = mock_model

        # Act
        provider = GeminiProvider()

        # Assert
        assert provider.api_key == "test_api_key"
        mock_configure.assert_called_once_with(api_key="test_api_key")
        mock_gen_model.assert_called_once_with('gemini-2.5-flash')

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_init_with_api_key_param(self, mock_gen_model, mock_configure):
        """Test initialization with API key passed as parameter."""
        # Arrange
        mock_model = MagicMock()
        mock_gen_model.return_value = mock_model

        # Act
        provider = GeminiProvider(api_key="direct_key")
        # Assert
        assert provider.api_key == "direct_key"
        mock_configure.assert_called_once_with(api_key="direct_key")
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises ValueError."""
        # Arrange & Act & Assert
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Gemini APIキーが設定されていません"):
                GeminiProvider()

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_optimize_content(self, mock_gen_model, mock_configure):
        """Test content optimization with default options."""
        # Arrange
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Optimized content"
        mock_model.generate_content.return_value = mock_response
        mock_gen_model.return_value = mock_model
        
        provider = GeminiProvider(api_key="test_key")
        
        # Act
        result = provider.optimize_content("Test content")
        
        # Assert
        assert result == "Optimized content"
        mock_model.generate_content.assert_called_once()
        call_args = mock_model.generate_content.call_args[0][0]
        assert "Test content" in call_args
        
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_optimize_content_with_custom_options(self, mock_gen_model, mock_configure):
        """Test content optimization with custom options."""
        # Arrange
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Optimized with custom options"
        mock_model.generate_content.return_value = mock_response
        mock_gen_model.return_value = mock_model
        
        provider = GeminiProvider(api_key="test_key")
        
        # Act
        result = provider.optimize_content(
            "Test content",
            options={
                "model": "custom-model",
                "temperature": 0.9,
                "max_tokens": 500
            }
        )
        
        # Assert
        assert result == "Optimized with custom options"
        # Check if model was updated
        mock_gen_model.assert_called_with("custom-model")
        # Check generation config
        gen_config = mock_model.generate_content.call_args[1]["generation_config"]
        assert gen_config.temperature == 0.9
        assert gen_config.max_output_tokens == 500

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_summary(self, mock_gen_model, mock_configure):
        """Test summary generation."""
        # Arrange
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a summary."
        mock_model.generate_content.return_value = mock_response
        mock_gen_model.return_value = mock_model
        
        provider = GeminiProvider(api_key="test_key")
        
        # Act
        result = provider.generate_summary("Long content " * 100, max_length=50)
        
        # Assert
        assert result == "This is a summary."
        call_args = mock_model.generate_content.call_args[0][0]
        assert "Long content" in call_args
        assert "50文字以内" in call_args

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_optimize_content_api_error(self, mock_gen_model, mock_configure):
        """Test handling of API errors during content optimization."""
        # Arrange
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = google_exceptions.GoogleAPIError("API error")
        mock_gen_model.return_value = mock_model
        
        provider = GeminiProvider(api_key="test_key")
        
        # Act & Assert
        with pytest.raises(google_exceptions.GoogleAPIError, match="API error"):
            provider.optimize_content("Test content")
