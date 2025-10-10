# Quick Start Guide

Get started with MarkitDown Chunker in 5 minutes!

## Installation

```bash
pip install markitdown-chunker
```

## Basic Usage

### 1. Simple Document Processing

Convert a document and chunk it with one line:

```python
from markitdown_chunker import MarkitDownProcessor

processor = MarkitDownProcessor()
result = processor.process("document.pdf", "output/")
```

That's it! Your document is now:
- ✅ Converted to markdown
- ✅ Split into intelligent chunks
- ✅ Exported as JSON with metadata

### 2. Command Line Usage

Even simpler - use the CLI:

```bash
markitdown-chunker document.pdf output/
```

### 3. Custom Chunk Size

Need larger or smaller chunks?

```python
processor = MarkitDownProcessor(
    chunk_size=2000,    # 2000 characters per chunk
    chunk_overlap=400   # 400 characters overlap
)
result = processor.process("document.pdf", "output/")
```

Or via CLI:

```bash
markitdown-chunker document.pdf output/ --chunk-size 2000 --overlap 400
```

## Common Use Cases

### Convert Multiple Documents

```python
processor = MarkitDownProcessor()
files = ["doc1.pdf", "doc2.docx", "doc3.pptx"]
results = processor.process_batch(files, "output/")
```

### Just Convert (No Chunking)

```bash
markitdown-chunker document.pdf output/ --convert-only
```

### Just Chunk Existing Markdown

```bash
markitdown-chunker document.md output/ --chunk-only
```

## Output Structure

After processing, you'll have:

```
output/
├── document.md              # Converted markdown
├── document_chunks.json     # Chunks with metadata
└── images/                  # Extracted images (if any)
    ├── image1.png
    └── image2.png
```

## What's in the Output?

After processing, you'll have:

```
output/
├── document.md              # Converted markdown
├── document_chunks.json     # Chunks with metadata
└── images/                  # Extracted images (if any)
    ├── page1_img1.png
    └── page2_img1.jpg
```

### JSON Structure

```json
{
  "source_info": {
    "source_file": "document.pdf",
    "markdown_file": "output/document.md",
    "images_dir": "output/images"
  },
  "chunks": [
    {
      "text": "Your content here...",
      "metadata": {
        "Header 1": "Introduction",
        "chunk_index": 0
      }
    }
  ],
  "total_chunks": 10,
  "statistics": {
    "total_characters": 12000,
    "avg_chunk_size": 1200
  }
}
```

## Supported Formats

- 📄 Documents: PDF, DOCX, DOC, TXT, MD, RTF, ODT
- 📊 Spreadsheets: XLSX, XLS, ODS
- 📽️ Presentations: PPTX, PPT, ODP
- 🌐 Web: HTML, HTM
- 🎵 Audio/Video: MP3, MP4, WAV (requires ffmpeg - see [docs](docs/FFMPEG_AUDIO.md))

## Next Steps

- 📖 Read the [full documentation](README.md)
- 💻 Check out [examples](examples/)
- 🐛 [Report issues](https://github.com/yourusername/markitdown-chunker/issues)

## Need Help?

```bash
# See all options
markitdown-chunker --help

# List supported formats
markitdown-chunker --list-formats
```

---

Happy chunking! 🚀

