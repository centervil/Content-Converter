"""Tests for the MarkdownParser class."""
import os
import pytest
from pathlib import Path
from content_converter.core.parser import MarkdownParser


def test_parse_file_with_frontmatter(tmp_path):
    """Test parsing a markdown file with frontmatter."""
    # Arrange
    content = """---
title: Test Title
author: Test Author
tags: [test, example]
---
# Test Content

This is a test content.
"""
    test_file = tmp_path / "test.md"
    test_file.write_text(content, encoding="utf-8")
    
    parser = MarkdownParser()
    
    # Act
    result = parser.parse_file(str(test_file))
    
    # Assert
    assert result["metadata"]["title"] == "Test Title"
    assert result["metadata"]["author"] == "Test Author"
    assert result["metadata"]["tags"] == ["test", "example"]
    assert "# Test Content" in result["content"]
    assert "This is a test content." in result["content"]


def test_parse_file_without_frontmatter(tmp_path):
    """Test parsing a markdown file without frontmatter."""
    # Arrange
    content = "# Test Content\n\nThis is a test content without frontmatter.\n"
    test_file = tmp_path / "test_no_frontmatter.md"
    test_file.write_text(content, encoding="utf-8")
    
    parser = MarkdownParser()
    
    # Act
    result = parser.parse_file(str(test_file))
    
    # Assert
    assert result["metadata"] == {}
    assert "# Test Content" in result["content"]
    assert "without frontmatter" in result["content"]


def test_parse_nonexistent_file():
    """Test parsing a non-existent file raises FileNotFoundError."""
    # Arrange
    parser = MarkdownParser()
    
    # Act & Assert
    with pytest.raises(FileNotFoundError):
        parser.parse_file("/nonexistent/path/to/file.md")


def test_parse_file_with_invalid_frontmatter(tmp_path):
    """Test parsing a file with invalid frontmatter falls back to content extraction."""
    # Arrange
    content = """---
invalid: yaml: : : :
---
# Test Invalid Frontmatter

This content should still be readable.
"""
    test_file = tmp_path / "test_invalid_frontmatter.md"
    test_file.write_text(content, encoding="utf-8")
    
    parser = MarkdownParser()
    
    # Act
    result = parser.parse_file(str(test_file))
    
    # Assert
    assert result["metadata"] == {}
    assert "# Test Invalid Frontmatter" in result["content"]
    assert "This content should still be readable" in result["content"]


def test_parse_file_with_only_frontmatter_markers(tmp_path):
    """Test parsing a file with only frontmatter markers and no content."""
    # Arrange
    content = "---\n---\n"
    test_file = tmp_path / "test_only_markers.md"
    test_file.write_text(content, encoding="utf-8")
    
    parser = MarkdownParser()
    
    # Act
    result = parser.parse_file(str(test_file))
    
    # Assert
    assert result["metadata"] == {}
    assert result["content"] == ""


def test_parse_file_with_unicode_content(tmp_path):
    """Test parsing a file with unicode characters."""
    # Arrange
    content = "---\ntitle: テストタイトル\n---\n# テストコンテンツ\n\nこれはテストです。\n"
    test_file = tmp_path / "test_unicode.md"
    test_file.write_text(content, encoding="utf-8")
    
    parser = MarkdownParser()
    
    # Act
    result = parser.parse_file(str(test_file))
    
    # Assert
    assert result["metadata"]["title"] == "テストタイトル"
    assert "# テストコンテンツ" in result["content"]
    assert "これはテストです。" in result["content"]
