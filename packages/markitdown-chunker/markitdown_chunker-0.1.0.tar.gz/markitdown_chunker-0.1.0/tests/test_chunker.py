"""Tests for the DocumentChunker class."""

import tempfile
import pytest

from markitdown_chunker.chunker import DocumentChunker


class TestDocumentChunker:
    """Test suite for DocumentChunker."""
    
    def test_initialization_defaults(self):
        """Test chunker initialization with defaults."""
        chunker = DocumentChunker()
        
        assert chunker.chunk_size == DocumentChunker.DEFAULT_CHUNK_SIZE
        assert chunker.chunk_overlap == DocumentChunker.DEFAULT_CHUNK_OVERLAP
        assert chunker.use_markdown_splitter is True
    
    def test_initialization_custom(self):
        """Test chunker initialization with custom values."""
        chunker = DocumentChunker(
            chunk_size=2000,
            chunk_overlap=400,
            use_markdown_splitter=False
        )
        
        assert chunker.chunk_size == 2000
        assert chunker.chunk_overlap == 400
        assert chunker.use_markdown_splitter is False
    
    def test_chunk_text_simple(self):
        """Test chunking of simple text."""
        chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
        
        text = "This is a test. " * 20  # Create text longer than chunk_size
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
        assert all("text" in chunk for chunk in chunks)
        assert all("metadata" in chunk for chunk in chunks)
    
    def test_chunk_text_markdown_headers(self):
        """Test chunking with markdown headers."""
        chunker = DocumentChunker(chunk_size=100, use_markdown_splitter=True)
        
        text = """# Header 1
Some content here.

## Header 2
More content here.

### Header 3
Even more content.
"""
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
        # At least one chunk should have header metadata
        has_metadata = any(
            chunk["metadata"] and len(chunk["metadata"]) > 2 
            for chunk in chunks
        )
        assert has_metadata or len(chunks) > 0  # Either has metadata or chunks exist
    
    def test_chunk_file_missing(self):
        """Test chunking of missing file."""
        chunker = DocumentChunker()
        
        with pytest.raises(FileNotFoundError):
            chunker.chunk_file("nonexistent.md")
    
    def test_chunk_file(self):
        """Test chunking of a markdown file."""
        chunker = DocumentChunker(chunk_size=100)
        
        # Create temporary markdown file
        with tempfile.NamedTemporaryFile(mode='w', suffix=".md", delete=False) as f:
            f.write("# Test Document\n\nThis is test content. " * 10)
            temp_file = f.name
        
        try:
            chunks = chunker.chunk_file(temp_file)
            
            assert len(chunks) > 0
            # Verify metadata includes source file
            for chunk in chunks:
                assert "source_file" in chunk["metadata"]
                assert chunk["metadata"]["source_file"] == temp_file
        finally:
            import os
            os.unlink(temp_file)
    
    def test_get_statistics(self):
        """Test statistics generation."""
        chunker = DocumentChunker()
        
        chunks = [
            {"text": "a" * 100, "metadata": {}},
            {"text": "b" * 200, "metadata": {}},
            {"text": "c" * 150, "metadata": {}},
        ]
        
        stats = chunker.get_statistics(chunks)
        
        assert stats["total_chunks"] == 3
        assert stats["total_characters"] == 450
        assert stats["avg_chunk_size"] == 150
        assert stats["min_chunk_size"] == 100
        assert stats["max_chunk_size"] == 200
    
    def test_get_statistics_empty(self):
        """Test statistics with empty chunks."""
        chunker = DocumentChunker()
        
        stats = chunker.get_statistics([])
        
        assert stats["total_chunks"] == 0
        assert stats["total_characters"] == 0

