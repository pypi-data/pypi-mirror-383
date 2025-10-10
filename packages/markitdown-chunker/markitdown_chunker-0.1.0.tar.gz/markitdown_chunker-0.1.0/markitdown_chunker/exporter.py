"""
Export chunks and metadata to various formats.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class JSONExporter:
    """
    Exports document chunks and metadata to JSON format.
    """
    
    def __init__(self, indent: int = 2, ensure_ascii: bool = False):
        """
        Initialize the JSONExporter.
        
        Args:
            indent: Number of spaces for JSON indentation
            ensure_ascii: Whether to escape non-ASCII characters
        """
        self.indent = indent
        self.ensure_ascii = ensure_ascii
    
    def export(
        self,
        chunks: List[Dict[str, Any]],
        output_path: str,
        include_metadata: bool = True,
        add_timestamp: bool = True
    ) -> str:
        """
        Export chunks to a JSON file.
        
        Args:
            chunks: List of chunk dictionaries
            output_path: Path to save the JSON file
            include_metadata: Whether to include chunk metadata
            add_timestamp: Whether to add export timestamp
            
        Returns:
            Path to the saved JSON file
        """
        # Prepare data structure
        export_data = {
            "chunks": chunks if include_metadata else [
                {"text": chunk["text"], "index": i} 
                for i, chunk in enumerate(chunks)
            ],
            "total_chunks": len(chunks)
        }
        
        # Add timestamp if requested
        if add_timestamp:
            export_data["exported_at"] = datetime.now().isoformat()
        
        # Add statistics
        if chunks:
            chunk_sizes = [len(chunk["text"]) for chunk in chunks]
            export_data["statistics"] = {
                "total_characters": sum(chunk_sizes),
                "avg_chunk_size": sum(chunk_sizes) / len(chunks),
                "min_chunk_size": min(chunk_sizes),
                "max_chunk_size": max(chunk_sizes)
            }
        
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=self.indent, ensure_ascii=self.ensure_ascii)
        
        return str(output_file)
    
    def export_with_source_info(
        self,
        chunks: List[Dict[str, Any]],
        output_path: str,
        source_info: Dict[str, Any]
    ) -> str:
        """
        Export chunks with additional source document information.
        
        Args:
            chunks: List of chunk dictionaries
            output_path: Path to save the JSON file
            source_info: Dictionary with source document information
            
        Returns:
            Path to the saved JSON file
        """
        export_data = {
            "source_info": source_info,
            "chunks": chunks,
            "total_chunks": len(chunks),
            "exported_at": datetime.now().isoformat()
        }
        
        # Add statistics
        if chunks:
            chunk_sizes = [len(chunk["text"]) for chunk in chunks]
            export_data["statistics"] = {
                "total_characters": sum(chunk_sizes),
                "avg_chunk_size": sum(chunk_sizes) / len(chunks),
                "min_chunk_size": min(chunk_sizes),
                "max_chunk_size": max(chunk_sizes)
            }
        
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=self.indent, ensure_ascii=self.ensure_ascii)
        
        return str(output_file)
    
    def export_batch(
        self,
        batch_data: List[Dict[str, Any]],
        output_dir: str,
        filename_prefix: str = "chunks"
    ) -> List[str]:
        """
        Export multiple chunk sets to separate JSON files.
        
        Args:
            batch_data: List of dictionaries, each containing 'chunks' and optional 'metadata'
            output_dir: Directory to save the JSON files
            filename_prefix: Prefix for the output filenames
            
        Returns:
            List of paths to saved JSON files
        """
        output_paths = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for i, data in enumerate(batch_data):
            filename = f"{filename_prefix}_{i+1}.json"
            filepath = output_path / filename
            
            chunks = data.get("chunks", [])
            metadata = data.get("metadata", {})
            
            if metadata:
                saved_path = self.export_with_source_info(chunks, str(filepath), metadata)
            else:
                saved_path = self.export(chunks, str(filepath))
            
            output_paths.append(saved_path)
        
        return output_paths
    
    @staticmethod
    def load(json_path: str) -> Dict[str, Any]:
        """
        Load chunks from a JSON file.
        
        Args:
            json_path: Path to the JSON file
            
        Returns:
            Dictionary containing chunks and metadata
            
        Raises:
            FileNotFoundError: If the JSON file doesn't exist
        """
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

