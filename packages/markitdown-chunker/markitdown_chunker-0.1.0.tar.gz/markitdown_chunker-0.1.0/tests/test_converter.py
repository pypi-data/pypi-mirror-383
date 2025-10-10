"""Tests for the MarkdownConverter class."""

import os
import tempfile
from pathlib import Path
import pytest

from markitdown_chunker.converter import MarkdownConverter


class TestMarkdownConverter:
    """Test suite for MarkdownConverter."""
    
    def test_initialization(self):
        """Test converter initialization."""
        converter = MarkdownConverter()
        assert converter is not None
        assert converter.markitdown is not None
    
    def test_is_supported(self):
        """Test format support checking."""
        converter = MarkdownConverter()
        
        # Test supported formats
        assert converter.is_supported("test.pdf")
        assert converter.is_supported("test.docx")
        assert converter.is_supported("test.md")
        assert converter.is_supported("TEST.PDF")  # Case insensitive
        
        # Test unsupported formats
        assert not converter.is_supported("test.xyz")
        assert not converter.is_supported("test.exe")
    
    def test_convert_missing_file(self):
        """Test conversion with missing file."""
        converter = MarkdownConverter()
        
        with pytest.raises(FileNotFoundError):
            converter.convert("nonexistent.pdf", "output/")
    
    def test_convert_unsupported_format(self):
        """Test conversion with unsupported format."""
        converter = MarkdownConverter()
        
        # Create a temporary file with unsupported format
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported file format"):
                converter.convert(temp_file, "output/")
        finally:
            os.unlink(temp_file)
    
    def test_convert_text_file(self):
        """Test conversion of a simple text file."""
        converter = MarkdownConverter()
        
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix=".txt", delete=False) as f:
            f.write("Hello, World!\n\nThis is a test document.")
            temp_file = f.name
        
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as output_dir:
            try:
                result = converter.convert(temp_file, output_dir)
                
                # Verify result structure
                assert "markdown_path" in result
                assert "markdown_content" in result
                assert "source_file" in result
                assert result["source_file"] == temp_file
                
                # Verify markdown file was created
                assert os.path.exists(result["markdown_path"])
                
                # Verify content
                with open(result["markdown_path"], 'r') as f:
                    content = f.read()
                    assert "Hello, World!" in content or "test document" in content
            finally:
                os.unlink(temp_file)

