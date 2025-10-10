"""
Example 1: Full Pipeline Processing

This example demonstrates how to run the complete pipeline:
- Convert document to markdown
- Chunk the markdown
- Export to JSON

All in one command!
"""

from markitdown_chunker import MarkitDownProcessor


def main():
    """Run the complete pipeline on a document."""
    print("=" * 60)
    print("Example 1: Full Pipeline Processing")
    print("=" * 60)
    print()
    
    # Create processor with custom settings
    processor = MarkitDownProcessor(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    print("✓ Processor created with:")
    print(f"  - Chunk size: 1000 characters")
    print(f"  - Overlap: 200 characters")
    print()
    
    # To use with a real file, uncomment and modify:
    """
    result = processor.process(
        file_path="sample.pdf",
        output_dir="output/"
    )
    
    print("✓ Processing complete!")
    print(f"  - Markdown: {result['conversion']['markdown_path']}")
    print(f"  - Chunks: {len(result['chunking']['chunks'])}")
    print(f"  - JSON: {result['export']['json_path']}")
    print()
    
    # Print statistics
    stats = result['chunking']['statistics']
    print("Statistics:")
    print(f"  - Total chunks: {stats['total_chunks']}")
    print(f"  - Total characters: {stats['total_characters']}")
    print(f"  - Average chunk size: {stats['avg_chunk_size']:.0f}")
    """
    
    print("📝 To run with your document:")
    print("   1. Uncomment the code above")
    print("   2. Replace 'sample.pdf' with your file path")
    print("   3. Run: python examples/example_01_full_pipeline.py")


if __name__ == "__main__":
    main()

