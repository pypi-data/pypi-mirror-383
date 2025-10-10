"""
Example 6: Advanced Usage Patterns

This example demonstrates advanced techniques:
- Using individual components directly
- Custom configuration per component
- Combining components in custom ways
- Advanced metadata handling
"""

from markitdown_chunker import (
    MarkdownConverter, 
    DocumentChunker, 
    JSONExporter
)


def main():
    """Demonstrate advanced usage patterns."""
    print("=" * 60)
    print("Example 6: Advanced Usage")
    print("=" * 60)
    print()
    
    # Pattern 1: Use components independently
    print("Pattern 1: Direct component usage")
    print("-" * 40)
    
    converter = MarkdownConverter()
    chunker = DocumentChunker(chunk_size=1500, chunk_overlap=300)
    exporter = JSONExporter(indent=4)
    
    print("✓ Created components independently")
    print(f"  - Converter: {converter.__class__.__name__}")
    print(f"  - Chunker: chunk_size={chunker.chunk_size}, overlap={chunker.chunk_overlap}")
    print(f"  - Exporter: indent={exporter.indent}")
    print()
    
    # Pattern 2: Check format support
    print("Pattern 2: Format validation")
    print("-" * 40)
    
    test_files = [
        "document.pdf",
        "presentation.pptx", 
        "spreadsheet.xlsx",
        "unknown.xyz"
    ]
    
    for file in test_files:
        is_supported = converter.is_supported(file)
        status = "✓ Supported" if is_supported else "✗ Not supported"
        print(f"  {status}: {file}")
    print()
    
    # Pattern 3: Chunk text directly
    print("Pattern 3: Direct text chunking")
    print("-" * 40)
    
    sample_text = """
# Data Science in 2024

## Introduction
Data science continues to evolve rapidly with new tools and techniques.

## Key Trends
Machine learning and AI are becoming more accessible to developers.

### Tools
Popular tools include Python, R, and various cloud platforms.

## Conclusion
The field is more exciting than ever with endless possibilities.
"""
    
    chunks = chunker.chunk_text(sample_text)
    print(f"✓ Chunked sample text into {len(chunks)} chunks")
    
    for i, chunk in enumerate(chunks):
        print(f"\n  Chunk {i+1}:")
        print(f"    Length: {len(chunk['text'])} chars")
        if chunk['metadata']:
            print(f"    Headers: {chunk['metadata']}")
    print()
    
    # Pattern 4: Custom metadata
    print("Pattern 4: Adding custom metadata")
    print("-" * 40)
    
    for chunk in chunks:
        chunk['metadata']['custom_field'] = 'my_value'
        chunk['metadata']['document_type'] = 'example'
        chunk['metadata']['author'] = 'demo'
    
    print("✓ Added custom metadata to all chunks:")
    print(f"  - custom_field")
    print(f"  - document_type")
    print(f"  - author")
    print()
    
    # Pattern 5: Get detailed statistics
    print("Pattern 5: Detailed statistics")
    print("-" * 40)
    
    stats = chunker.get_statistics(chunks)
    print("✓ Chunk statistics:")
    print(f"  - Total chunks: {stats['total_chunks']}")
    print(f"  - Total characters: {stats['total_characters']}")
    print(f"  - Average size: {stats['avg_chunk_size']:.1f} chars")
    print(f"  - Min size: {stats['min_chunk_size']} chars")
    print(f"  - Max size: {stats['max_chunk_size']} chars")
    print()
    
    # Pattern 6: Export with custom source info
    print("Pattern 6: Export with enhanced metadata")
    print("-" * 40)
    
    source_info = {
        'source_file': 'example.md',
        'processed_by': 'advanced_example',
        'custom_field_1': 'value1',
        'custom_field_2': 'value2'
    }
    
    # Uncomment to actually export:
    """
    json_path = exporter.export_with_source_info(
        chunks=chunks,
        output_path="output/advanced_example.json",
        source_info=source_info
    )
    print(f"✓ Exported to: {json_path}")
    """
    
    print("✓ Custom source info prepared for export")
    print()
    
    print("💡 Advanced tips:")
    print("   - Use components directly for maximum flexibility")
    print("   - Validate formats before processing")
    print("   - Add custom metadata for your use case")
    print("   - Chain operations in custom ways")
    print("   - Adjust parameters per document type")


if __name__ == "__main__":
    main()

