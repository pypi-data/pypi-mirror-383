"""
Main processor that orchestrates the entire pipeline.
"""

import os
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List

from .converter import MarkdownConverter
from .chunker import DocumentChunker
from .exporter import JSONExporter


class MarkitDownProcessor:
    """
    Main processor that orchestrates document conversion, chunking, and export.
    
    This class provides a unified interface to run the complete pipeline or
    individual steps as needed.
    """
    
    def __init__(
        self,
        chunk_size: int = DocumentChunker.DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DocumentChunker.DEFAULT_CHUNK_OVERLAP,
        use_markdown_splitter: bool = True,
        json_indent: int = 2
    ):
        """
        Initialize the MarkitDownProcessor.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
            use_markdown_splitter: Whether to use markdown-aware splitting
            json_indent: Number of spaces for JSON indentation
        """
        self.converter = MarkdownConverter()
        self.chunker = DocumentChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            use_markdown_splitter=use_markdown_splitter
        )
        self.exporter = JSONExporter(indent=json_indent)
    
    def process(
        self,
        file_path: str,
        output_dir: str,
        save_images: bool = True,
        include_image_summaries: bool = False,
        image_summarizer: Optional[Callable[[str], str]] = None,
        skip_conversion: bool = False,
        skip_chunking: bool = False,
        skip_export: bool = False
    ) -> Dict[str, Any]:
        """
        Process a document through the complete pipeline.
        
        Args:
            file_path: Path to the input file
            output_dir: Directory to save outputs
            save_images: Whether to save extracted images (conversion step)
            include_image_summaries: Whether to include image summaries in chunks
            image_summarizer: Optional function to summarize images
            skip_conversion: Skip conversion step (use existing markdown)
            skip_chunking: Skip chunking step (only convert)
            skip_export: Skip export step (only convert and chunk)
            
        Returns:
            Dictionary with results from each step
            
        Raises:
            FileNotFoundError: If the input file doesn't exist
            ValueError: If invalid options are provided
        """
        results = {
            "input_file": file_path,
            "output_dir": output_dir,
            "steps_completed": []
        }
        
        markdown_path = file_path
        markdown_content = None
        
        # Step 1: Conversion
        if not skip_conversion:
            conversion_result = self.converter.convert(
                file_path=file_path,
                output_dir=output_dir,
                save_images=save_images
            )
            results["conversion"] = conversion_result
            results["steps_completed"].append("conversion")
            markdown_path = conversion_result["markdown_path"]
            markdown_content = conversion_result["markdown_content"]
        else:
            # If skipping conversion, file_path should be a markdown file
            if not file_path.endswith('.md'):
                raise ValueError(
                    "When skipping conversion, input file must be a markdown file"
                )
            markdown_path = file_path
            with open(markdown_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
        
        if skip_chunking:
            return results
        
        # Step 2: Chunking
        chunks = self.chunker.chunk_file(
            markdown_path=markdown_path,
            include_images=include_image_summaries,
            image_summarizer=image_summarizer
        )
        
        results["chunking"] = {
            "chunks": chunks,
            "statistics": self.chunker.get_statistics(chunks)
        }
        results["steps_completed"].append("chunking")
        
        if skip_export:
            return results
        
        # Step 3: Export
        input_filename = Path(file_path).stem
        json_filename = f"{input_filename}_chunks.json"
        json_path = os.path.join(output_dir, json_filename)
        
        source_info = {
            "source_file": file_path,
            "markdown_file": markdown_path,
            "output_dir": output_dir
        }
        
        if "conversion" in results:
            source_info.update({
                "images_dir": results["conversion"].get("images_dir")
            })
        
        export_path = self.exporter.export_with_source_info(
            chunks=chunks,
            output_path=json_path,
            source_info=source_info
        )
        
        results["export"] = {
            "json_path": export_path
        }
        results["steps_completed"].append("export")
        
        return results
    
    def convert_only(
        self,
        file_path: str,
        output_dir: str,
        save_images: bool = True
    ) -> Dict[str, Any]:
        """
        Run only the conversion step.
        
        Args:
            file_path: Path to the input file
            output_dir: Directory to save outputs
            save_images: Whether to save extracted images
            
        Returns:
            Conversion results
        """
        return self.process(
            file_path=file_path,
            output_dir=output_dir,
            save_images=save_images,
            skip_chunking=True,
            skip_export=True
        )
    
    def chunk_only(
        self,
        markdown_path: str,
        include_image_summaries: bool = False,
        image_summarizer: Optional[Callable[[str], str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Run only the chunking step on an existing markdown file.
        
        Args:
            markdown_path: Path to the markdown file
            include_image_summaries: Whether to include image summaries
            image_summarizer: Optional function to summarize images
            
        Returns:
            List of chunks
        """
        return self.chunker.chunk_file(
            markdown_path=markdown_path,
            include_images=include_image_summaries,
            image_summarizer=image_summarizer
        )
    
    def export_only(
        self,
        chunks: List[Dict[str, Any]],
        output_path: str,
        source_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Run only the export step.
        
        Args:
            chunks: List of chunk dictionaries
            output_path: Path to save the JSON file
            source_info: Optional source information to include
            
        Returns:
            Path to the saved JSON file
        """
        if source_info:
            return self.exporter.export_with_source_info(
                chunks=chunks,
                output_path=output_path,
                source_info=source_info
            )
        else:
            return self.exporter.export(
                chunks=chunks,
                output_path=output_path
            )
    
    def process_batch(
        self,
        file_paths: List[str],
        output_dir: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Process multiple documents.
        
        Args:
            file_paths: List of paths to input files
            output_dir: Directory to save outputs
            **kwargs: Additional arguments to pass to process()
            
        Returns:
            List of result dictionaries
        """
        results = []
        for file_path in file_paths:
            try:
                result = self.process(file_path, output_dir, **kwargs)
                results.append(result)
            except Exception as e:
                results.append({
                    "error": str(e),
                    "input_file": file_path
                })
        return results

