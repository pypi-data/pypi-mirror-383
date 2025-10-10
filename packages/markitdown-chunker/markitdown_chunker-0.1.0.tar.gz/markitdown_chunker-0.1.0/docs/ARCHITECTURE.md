# Architecture Documentation

This document describes the architecture and design decisions of the MarkitDown Chunker package.

## Overview

MarkitDown Chunker is designed as a modular pipeline with three main stages:

1. **Conversion**: Document → Markdown
2. **Chunking**: Markdown → Chunks
3. **Export**: Chunks → JSON

## Package Structure

```
markitdown_chunker/
├── __init__.py          # Package exports
├── converter.py         # Step 1: Document conversion
├── chunker.py           # Step 2: Text chunking
├── exporter.py          # Step 3: Data export
├── processor.py         # Pipeline orchestration
└── cli.py               # Command-line interface
```

## Core Components

### 1. MarkdownConverter (`converter.py`)

**Purpose**: Convert various document formats to Markdown using the markitdown library.

**Key Features**:
- Format validation
- Image extraction and referencing
- Batch conversion support

**Dependencies**:
- `markitdown`: Microsoft's document conversion library

**Design Decisions**:
- Uses markitdown as the conversion engine (battle-tested, maintained)
- Returns structured dict with paths and content for flexibility
- Handles images automatically through markitdown's built-in support

### 2. DocumentChunker (`chunker.py`)

**Purpose**: Split markdown documents into intelligent chunks using LangChain text splitters.

**Key Features**:
- Markdown-aware splitting (respects headers)
- Recursive character splitting
- Configurable chunk size and overlap
- Optional image summarization

**Dependencies**:
- `langchain.text_splitter`: For text splitting algorithms

**Design Decisions**:
- Two-stage splitting approach:
  1. Split by markdown headers (preserve structure)
  2. Apply recursive splitting to large sections (ensure size limits)
- Metadata preservation through the pipeline
- Flexible image handling with user-provided summarizer

**Algorithm**:

```python
if use_markdown_splitter:
    1. Split by headers (# ## ###)
    2. For each section:
        a. Apply recursive splitting if > chunk_size
        b. Attach header metadata to chunks
else:
    1. Apply recursive character splitting only
```

### 3. JSONExporter (`exporter.py`)

**Purpose**: Export chunks with metadata to JSON format.

**Key Features**:
- Structured JSON output
- Automatic statistics generation
- Timestamp tracking
- Batch export support

**Design Decisions**:
- JSON chosen for:
  - Universal compatibility
  - Human-readable
  - Easy to parse
  - Supports complex metadata
- Statistics calculated at export time (avg, min, max chunk sizes)

### 4. MarkitDownProcessor (`processor.py`)

**Purpose**: Orchestrate the complete pipeline and provide a unified API.

**Key Features**:
- Full pipeline execution
- Individual step execution
- Batch processing
- Flexible configuration

**Design Decisions**:
- Composition over inheritance (uses converter, chunker, exporter)
- Skip flags for flexible pipeline control
- Consistent return format across methods
- Error handling at processor level

**API Design**:

```python
# Full pipeline
process(file_path, output_dir, **options)

# Individual steps
convert_only(file_path, output_dir)
chunk_only(markdown_path)
export_only(chunks, output_path)

# Batch processing
process_batch(file_paths, output_dir)
```

### 5. CLI (`cli.py`)

**Purpose**: Provide command-line access to all features.

**Design Decisions**:
- Mutually exclusive mode flags (--convert-only, --chunk-only)
- Sensible defaults for all parameters
- Verbose mode for debugging
- List formats utility

## Data Flow

```
Input File
    ↓
[MarkdownConverter]
    ↓
Markdown File + Images
    ↓
[DocumentChunker]
    ↓
Chunks with Metadata
    ↓
[JSONExporter]
    ↓
JSON File
```

## Configuration

### Default Values

```python
# Chunking
DEFAULT_CHUNK_SIZE = 1000        # characters
DEFAULT_CHUNK_OVERLAP = 200      # characters

# Headers to split on
DEFAULT_HEADERS = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

# JSON formatting
DEFAULT_JSON_INDENT = 2
```

### Rationale

- **Chunk Size (1000)**: Balances context preservation with processing efficiency
  - Large enough for meaningful content
  - Small enough for most embedding models
  - Common in RAG applications

- **Overlap (200)**: 20% of chunk size
  - Prevents information loss at boundaries
  - Standard practice in text chunking

- **Headers**: First three levels
  - Most documents use H1-H3
  - Deeper nesting is rare
  - Can be customized by user

## Extension Points

### Custom Image Summarization

Users can provide their own image summarization function:

```python
def my_summarizer(image_path: str) -> str:
    # Custom logic (AI vision, OCR, etc.)
    return summary

processor.process(
    file_path="doc.pdf",
    output_dir="output/",
    include_image_summaries=True,
    image_summarizer=my_summarizer
)
```

### Custom Text Splitters

Users can instantiate DocumentChunker with custom parameters:

```python
chunker = DocumentChunker(
    chunk_size=2000,
    chunk_overlap=400,
    headers_to_split_on=[
        ("#", "Title"),
        ("##", "Section"),
        ("###", "Subsection"),
        ("####", "Paragraph"),
    ]
)
```

## Error Handling

### Principles

1. **Fail Fast**: Validate inputs early
2. **Informative Errors**: Clear messages with context
3. **Graceful Degradation**: Batch operations continue on individual failures
4. **User Control**: Verbose mode for debugging

### Error Types

- `FileNotFoundError`: Missing input files
- `ValueError`: Invalid parameters or unsupported formats
- `Exception`: Catch-all for processing errors in batch mode

## Performance Considerations

### Memory

- Files are read once and processed in stages
- Chunks are kept in memory (acceptable for most documents)
- Large documents may benefit from streaming (future enhancement)

### Speed

- Document conversion is I/O bound (markitdown handles this)
- Chunking is CPU bound but fast (LangChain is optimized)
- JSON export is I/O bound (Python's json module is fast)

### Scalability

- Single file processing is synchronous
- Batch processing is sequential (parallelization possible in future)
- Suitable for:
  - ✅ Individual document processing
  - ✅ Small to medium batch jobs (< 100 files)
  - ⚠️ Large-scale processing (consider parallelization)

## Testing Strategy

### Unit Tests

- Test each component independently
- Mock external dependencies (markitdown, langchain)
- Cover edge cases (empty files, large files, malformed input)

### Integration Tests

- Test complete pipeline
- Use real files (small samples)
- Verify output structure and content

### Test Coverage Goals

- Core modules: > 90%
- CLI: > 70%
- Overall: > 85%

## Future Enhancements

### Planned

1. **Streaming Support**: Process large files without loading into memory
2. **Parallel Processing**: Batch processing with multiprocessing
3. **More Export Formats**: CSV, Parquet, JSONL
4. **Semantic Chunking**: Use embeddings to find natural boundaries
5. **Vector DB Integration**: Direct export to Pinecone, Weaviate, etc.
6. **Progress Callbacks**: Real-time progress reporting
7. **Caching**: Cache conversions to avoid redundant work

### Under Consideration

- Web API (FastAPI/Flask)
- Docker support
- Cloud storage integration
- Streaming API for large files
- Plugin system for custom processors

## Dependencies

### Core

- `markitdown`: Document conversion
- `langchain`: Text splitting algorithms
- `langchain-text-splitters`: Specialized splitters

### Development

- `pytest`: Testing framework
- `black`: Code formatting
- `flake8`: Linting
- `mypy`: Type checking

### Dependency Philosophy

- **Minimize dependencies**: Only include what's necessary
- **Prefer maintained libraries**: Choose popular, well-maintained packages
- **Pin major versions**: Allow minor/patch updates
- **Document alternatives**: Note why choices were made

## Security Considerations

### Input Validation

- Validate file formats before processing
- Check file existence before operations
- Sanitize user-provided paths

### File System Access

- Create directories with appropriate permissions
- Handle path traversal attacks (use Path.resolve())
- Clean up temporary files

### Data Privacy

- No telemetry or tracking
- All processing is local
- User controls all outputs

## Versioning

Following Semantic Versioning (SemVer):

- **Major**: Breaking API changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes

## Conclusion

MarkitDown Chunker is designed to be:

- **Modular**: Each component has a single responsibility
- **Flexible**: Run steps individually or as a pipeline
- **Extensible**: Easy to add new features or customize behavior
- **User-Friendly**: Simple API and CLI for common tasks
- **Maintainable**: Clean code, good tests, comprehensive docs

The architecture supports both simple use cases (process one document) and advanced scenarios (batch processing, custom chunking strategies, image summarization).

