"""
MarkitDown Chunker - A powerful document processing pipeline
Converts documents to markdown, chunks them, and exports structured data.
"""

import warnings

# Suppress pydub ffmpeg warning - not needed for document processing
warnings.filterwarnings("ignore", message=".*Couldn't find ffmpeg or avconv.*", category=RuntimeWarning)

from .converter import MarkdownConverter
from .chunker import DocumentChunker
from .exporter import JSONExporter
from .processor import MarkitDownProcessor

__version__ = "0.1.0"
__all__ = [
    "MarkdownConverter",
    "DocumentChunker", 
    "JSONExporter",
    "MarkitDownProcessor"
]

