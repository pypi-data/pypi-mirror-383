# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Support for more document formats
- Advanced chunking strategies (semantic, sentence-based)
- Integration with vector databases
- Web UI for document processing
- Cloud storage integration (S3, GCS, Azure)
- Parallel batch processing
- Custom output formats (CSV, Parquet, etc.)

## [0.1.0] - 2025-10-09

### Added
- Initial release of MarkitDown Chunker
- Document to Markdown conversion using markitdown
- Support for 15+ file formats (PDF, DOCX, PPTX, XLSX, HTML, etc.)
- Intelligent text chunking with LangChain
  - Recursive character text splitter
  - Markdown header-based text splitter
  - Configurable chunk size and overlap
- JSON export with metadata and statistics
- Command-line interface (CLI)
- Python API for programmatic usage
- Flexible pipeline execution
  - Run complete pipeline
  - Execute individual steps
  - Batch processing support
- Image extraction and referencing
- Optional image summarization support
- Comprehensive documentation and examples
- Unit tests for core functionality

### Features
- `MarkdownConverter`: Convert documents to markdown
- `DocumentChunker`: Split markdown into intelligent chunks
- `JSONExporter`: Export chunks with metadata
- `MarkitDownProcessor`: Orchestrate the complete pipeline
- CLI tool: `markitdown-chunker` command

### Supported File Formats
- Documents: .pdf, .docx, .doc, .txt, .md, .rtf, .odt
- Spreadsheets: .xlsx, .xls, .ods
- Presentations: .pptx, .ppt, .odp
- Web: .html, .htm

[Unreleased]: https://github.com/yourusername/markitdown-chunker/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/markitdown-chunker/releases/tag/v0.1.0

