# Image Extraction Guide

## Overview

MarkitDown Chunker supports automatic image extraction from PDF, DOCX, and PPTX files. Images are saved to a separate directory and referenced in the markdown output.

## Installation

### Basic Installation (No Image Extraction)

```bash
pip install markitdown-chunker
```

This installs the core functionality. Images will NOT be extracted, but text conversion works perfectly.

### With Image Extraction Support

```bash
pip install markitdown-chunker[images]
```

This installs additional libraries needed for image extraction:
- **PyMuPDF** - Extract images from PDF files
- **python-docx** - Extract images from DOCX files
- **python-pptx** - Extract images from PPTX files

### Manual Installation

You can also install image extraction libraries individually:

```bash
pip install pymupdf          # For PDF
pip install python-docx       # For DOCX
pip install python-pptx       # For PPTX
```

## How It Works

When `save_images=True` (default), the converter:

1. **Extracts images** from the document based on file type
2. **Saves them** to an `images/` subdirectory
3. **Updates markdown** to reference the extracted images
4. **Adds image section** at the end of the markdown file

## Supported Formats

| Format | Library Required | Image Extraction |
|--------|------------------|------------------|
| PDF    | pymupdf          | ✅ Full support   |
| DOCX   | python-docx      | ✅ Full support   |
| PPTX   | python-pptx      | ✅ Full support   |
| Other  | -                | ⚠️ Not applicable |

## Usage Examples

### Basic Usage

```python
from markitdown_chunker import MarkitDownProcessor

processor = MarkitDownProcessor()

# Images extracted by default
result = processor.process(
    file_path="document.pdf",
    output_dir="output/"
)

# Check extracted images
if result['conversion']['extracted_images']:
    print(f"Extracted {len(result['conversion']['extracted_images'])} images")
    for img in result['conversion']['extracted_images']:
        print(f"  - {img['filename']}")
```

### Disable Image Extraction

```python
# Don't extract images
result = processor.process(
    file_path="document.pdf",
    output_dir="output/",
    save_images=False
)
```

### Check Image Extraction Status

```python
from markitdown_chunker import MarkdownConverter

converter = MarkdownConverter()

result = converter.convert(
    file_path="presentation.pptx",
    output_dir="output/",
    save_images=True
)

# Check results
print(f"Images directory: {result['images_dir']}")
print(f"Extracted images: {len(result['extracted_images'])}")

for img in result['extracted_images']:
    print(f"  Slide {img['slide']}: {img['filename']}")
```

## Output Structure

After processing a document with images:

```
output/
├── document.md              # Markdown with image references
└── images/                  # Extracted images
    ├── page1_img1.png
    ├── page2_img1.jpg
    ├── page3_img1.png
    └── page3_img2.jpg
```

## Markdown Output Format

Images are added to the markdown in an "Extracted Images" section:

```markdown
# Document Title

Document content here...

## Extracted Images

![Page 1 Image 1](images/page1_img1.png)

![Page 2 Image 1](images/page2_img1.jpg)

![Page 3 Image 1](images/page3_img1.png)
```

## Image Naming Conventions

### PDF Images
- Format: `page{N}_img{M}.{ext}`
- Example: `page1_img1.png`, `page2_img3.jpg`

### DOCX Images
- Format: `docx_img{N}.{ext}`
- Example: `docx_img1.jpg`, `docx_img2.png`

### PPTX Images
- Format: `slide{N}_img{M}.{ext}`
- Example: `slide1_img1.png`, `slide3_img2.jpg`

## Troubleshooting

### No Images Extracted

**Problem**: Images aren't being extracted from your document.

**Solutions**:
1. Install image extraction libraries:
   ```bash
   pip install markitdown-chunker[images]
   ```

2. Check if the document actually contains images

3. Check console output for warnings:
   ```
   Info: Install 'pymupdf' for PDF image extraction
   ```

### Import Errors

**Problem**: `ImportError: No module named 'fitz'`

**Solution**:
```bash
pip install pymupdf
```

**Problem**: `ImportError: No module named 'docx'`

**Solution**:
```bash
pip install python-docx
```

### Partial Extraction

**Problem**: Some images are missing.

**Possible causes**:
- Inline images vs. embedded images (different extraction methods)
- Corrupted image data in the document
- Unsupported image formats in the document

**Check**:
```python
result = converter.convert(file_path, output_dir)
print(f"Extraction warnings: {result.get('warnings', [])}")
```

## Performance Considerations

### Large Documents

For documents with many images:
- Extraction adds processing time (usually < 1 second per image)
- Disk space increases (original image quality preserved)
- Memory usage is reasonable (images processed one at a time)

### Batch Processing

When processing multiple documents:

```python
processor = MarkitDownProcessor()

files = ["doc1.pdf", "doc2.docx", "doc3.pptx"]
results = processor.process_batch(
    file_paths=files,
    output_dir="output/",
    save_images=True
)

# Count total images
total_images = sum(
    len(r.get('conversion', {}).get('extracted_images', []))
    for r in results
    if 'conversion' in r
)
print(f"Total images extracted: {total_images}")
```

## Advanced Configuration

### Custom Image Processing

If you need custom image processing:

```python
from markitdown_chunker import MarkdownConverter
from PIL import Image

converter = MarkdownConverter()

# Extract images
result = converter.convert("document.pdf", "output/")

# Process extracted images
for img_info in result['extracted_images']:
    img_path = img_info['path']
    
    # Open with PIL for processing
    with Image.open(img_path) as img:
        # Resize, compress, convert, etc.
        img.thumbnail((800, 800))
        img.save(img_path, optimize=True, quality=85)
```

### Selective Image Extraction

Extract only specific file types:

```python
def process_with_selective_images(file_path, output_dir):
    ext = file_path.lower().split('.')[-1]
    
    # Only extract from PDFs
    save_images = (ext == 'pdf')
    
    processor = MarkitDownProcessor()
    return processor.process(
        file_path=file_path,
        output_dir=output_dir,
        save_images=save_images
    )
```

## Best Practices

1. **Install image libraries** if you regularly process documents with images

2. **Check extraction results** to verify images were found:
   ```python
   if not result['conversion']['extracted_images']:
       print("No images found in document")
   ```

3. **Use appropriate storage** for image-heavy documents

4. **Consider disk space** when batch processing many documents

5. **Validate image paths** in markdown if moving files around

## FAQ

**Q: Do I need image extraction for chunking?**
A: No, chunking works with or without images. Images just enhance the output.

**Q: Are original images modified?**
A: No, images are extracted as-is from the source document.

**Q: What if my PDF has vector graphics?**
A: Vector graphics embedded as images are extracted. Native vector elements may not be captured.

**Q: Can I extract images without using markitdown-chunker?**
A: Yes, you can use PyMuPDF, python-docx, or python-pptx directly for just image extraction.

**Q: Do images affect chunk size?**
A: No, image markdown references are just text. The actual image files are separate.

## See Also

- [Main README](../README.md)
- [Installation Guide](../INSTALL.md)
- [Architecture Documentation](ARCHITECTURE.md)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [python-pptx Documentation](https://python-pptx.readthedocs.io/)

