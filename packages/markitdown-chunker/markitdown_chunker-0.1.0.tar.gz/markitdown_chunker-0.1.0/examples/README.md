# Examples

This directory contains example scripts demonstrating various use cases of markitdown-chunker.

## Running the Examples

First, make sure you have markitdown-chunker installed:

```bash
pip install markitdown-chunker
```

Or if you're developing locally:

```bash
cd /path/to/markitdown-chunker
pip install -e .
```

## Available Examples

Each example is in its own file for clarity and ease of use.

### Example 1: Full Pipeline Processing
**File:** `example_01_full_pipeline.py`

Run the complete pipeline (convert → chunk → export) in one command.

```bash
python examples/example_01_full_pipeline.py
```

**What you'll learn:**
- How to process a document end-to-end
- Basic configuration options
- Understanding the output structure

---

### Example 2: Step-by-Step Processing
**File:** `example_02_step_by_step.py`

Execute each pipeline step independently for maximum control.

```bash
python examples/example_02_step_by_step.py
```

**What you'll learn:**
- Running conversion only
- Running chunking only
- Running export only
- Benefits of step-by-step approach

---

### Example 3: Custom Chunking
**File:** `example_03_custom_chunking.py`

Customize chunking behavior with different parameters.

```bash
python examples/example_03_custom_chunking.py
```

**What you'll learn:**
- Custom chunk sizes and overlap
- Markdown header-based splitting
- Direct text chunking
- Getting chunk statistics

---

### Example 4: Batch Processing
**File:** `example_04_batch_processing.py`

Process multiple documents at once.

```bash
python examples/example_04_batch_processing.py
```

**What you'll learn:**
- Processing multiple files
- Error handling in batch mode
- Automated document workflows

---

### Example 5: Image Summarization
**File:** `example_05_image_summarization.py`

Include AI-powered image descriptions in your chunks.

```bash
python examples/example_05_image_summarization.py
```

**What you'll learn:**
- Integrating vision models
- Processing images in documents
- Adding image descriptions to chunks

---

### Example 6: Advanced Usage
**File:** `example_06_advanced_usage.py`

Advanced patterns using individual components.

```bash
python examples/example_06_advanced_usage.py
```

**What you'll learn:**
- Using components directly
- Custom metadata handling
- Format validation
- Advanced configuration

---

## Quick Reference

| Example | Use Case | Difficulty |
|---------|----------|------------|
| 01 | Full pipeline | ⭐ Beginner |
| 02 | Step-by-step control | ⭐⭐ Intermediate |
| 03 | Custom chunking | ⭐⭐ Intermediate |
| 04 | Batch processing | ⭐⭐ Intermediate |
| 05 | Image summarization | ⭐⭐⭐ Advanced |
| 06 | Advanced patterns | ⭐⭐⭐ Advanced |

## Creating Your Own Examples

You can use these examples as templates for your own use cases. Simply:

1. Copy an example file
2. Modify the file paths and parameters
3. Add your custom logic
4. Run and test

### Quick Template

```python
from markitdown_chunker import MarkitDownProcessor

# Create processor
processor = MarkitDownProcessor(
    chunk_size=1000,
    chunk_overlap=200
)

# Process your document
result = processor.process(
    file_path="your_document.pdf",
    output_dir="output/"
)

print(f"Processed successfully!")
print(f"Created {len(result['chunking']['chunks'])} chunks")
```

## Need Help?

- 📖 See main [README.md](../README.md) for full documentation
- 🚀 Check [QUICKSTART.md](../QUICKSTART.md) for quick start guide
- 🏗️ Read [ARCHITECTURE.md](../docs/ARCHITECTURE.md) for technical details

