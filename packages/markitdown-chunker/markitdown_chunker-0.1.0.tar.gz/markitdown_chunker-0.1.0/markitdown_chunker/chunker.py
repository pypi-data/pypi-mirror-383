"""
Document chunker using LangChain text splitters.
"""

import os
from typing import List, Dict, Optional, Callable, Any
from pathlib import Path
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter, 
    MarkdownHeaderTextSplitter
)


class DocumentChunker:
    """
    Chunks markdown documents using LangChain text splitters.
    
    Supports both recursive character splitting and markdown header-based splitting.
    """
    
    # Default values
    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_CHUNK_OVERLAP = 200
    
    # Default markdown headers to split on
    DEFAULT_HEADERS = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    
    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        use_markdown_splitter: bool = True,
        headers_to_split_on: Optional[List[tuple]] = None
    ):
        """
        Initialize the DocumentChunker.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
            use_markdown_splitter: Whether to use markdown-aware splitting
            headers_to_split_on: List of (header_marker, header_name) tuples
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_markdown_splitter = use_markdown_splitter
        self.headers_to_split_on = headers_to_split_on or self.DEFAULT_HEADERS
        
        # Initialize splitters
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        if use_markdown_splitter:
            self.markdown_splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on=self.headers_to_split_on,
                strip_headers=False
            )
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunk a text string.
        
        Args:
            text: The text to chunk
            
        Returns:
            List of dictionaries containing chunk text and metadata
        """
        chunks = []
        
        if self.use_markdown_splitter:
            # First split by markdown headers
            md_header_splits = self.markdown_splitter.split_text(text)
            
            # Then apply recursive splitting to each section
            for doc in md_header_splits:
                # Get the metadata from markdown headers
                header_metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                
                # Split large sections further
                sub_chunks = self.recursive_splitter.split_text(
                    doc.page_content if hasattr(doc, 'page_content') else str(doc)
                )
                
                for i, chunk_text in enumerate(sub_chunks):
                    chunks.append({
                        "text": chunk_text,
                        "metadata": {
                            **header_metadata,
                            "sub_chunk_index": i,
                            "total_sub_chunks": len(sub_chunks)
                        }
                    })
        else:
            # Use only recursive splitting
            split_chunks = self.recursive_splitter.split_text(text)
            for i, chunk_text in enumerate(split_chunks):
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "chunk_index": i,
                        "total_chunks": len(split_chunks)
                    }
                })
        
        return chunks
    
    def chunk_file(
        self, 
        markdown_path: str,
        include_images: bool = False,
        image_summarizer: Optional[Callable[[str], str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk a markdown file.
        
        Args:
            markdown_path: Path to the markdown file
            include_images: Whether to process images in the markdown
            image_summarizer: Optional function that takes image path and returns summary
            
        Returns:
            List of chunk dictionaries
            
        Raises:
            FileNotFoundError: If the markdown file doesn't exist
        """
        if not os.path.exists(markdown_path):
            raise FileNotFoundError(f"Markdown file not found: {markdown_path}")
        
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Process images if requested
        if include_images and image_summarizer:
            content = self._process_images(content, markdown_path, image_summarizer)
        
        chunks = self.chunk_text(content)
        
        # Add file metadata to all chunks
        for chunk in chunks:
            chunk["metadata"]["source_file"] = markdown_path
            chunk["metadata"]["chunk_size_config"] = self.chunk_size
            chunk["metadata"]["chunk_overlap_config"] = self.chunk_overlap
        
        return chunks
    
    def _process_images(
        self, 
        content: str, 
        markdown_path: str,
        image_summarizer: Callable[[str], str]
    ) -> str:
        """
        Process images in markdown content by adding summaries.
        
        Args:
            content: Markdown content
            markdown_path: Path to the markdown file (for resolving relative image paths)
            image_summarizer: Function to summarize images
            
        Returns:
            Modified markdown content with image summaries
        """
        import re
        
        # Find all image references: ![alt text](image_path)
        image_pattern = r'!\[(.*?)\]\((.*?)\)'
        
        def replace_image(match):
            alt_text = match.group(1)
            image_path = match.group(2)
            
            # Resolve relative paths
            if not os.path.isabs(image_path):
                markdown_dir = os.path.dirname(markdown_path)
                image_path = os.path.join(markdown_dir, image_path)
            
            # Get summary if image exists
            summary = alt_text  # Default to alt text
            if os.path.exists(image_path):
                try:
                    summary = image_summarizer(image_path)
                except Exception as e:
                    summary = f"{alt_text} (summarization failed: {str(e)})"
            
            # Return enhanced markdown
            return f"![{alt_text}]({match.group(2)})\n\n**Image Description:** {summary}\n"
        
        return re.sub(image_pattern, replace_image, content)
    
    def get_statistics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Dictionary with statistics
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "total_characters": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0
            }
        
        chunk_sizes = [len(chunk["text"]) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "total_characters": sum(chunk_sizes),
            "avg_chunk_size": sum(chunk_sizes) / len(chunks),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes)
        }

