"""
Example 2: Step-by-Step Processing

This example shows how to run each step of the pipeline independently:
1. Convert document to markdown
2. Chunk the markdown 
3. Export chunks to JSON

This gives you more control over each stage.
"""

from markitdown_chunker import MarkitDownProcessor


def main():
    """Run each step of the pipeline separately."""
    print("=" * 60)
    print("Example 2: Step-by-Step Processing")
    print("=" * 60)
    print()
    
    processor = MarkitDownProcessor()
    
    print("Running pipeline steps independently...")
    print()
    
    # To use with a real file, uncomment and modify:
    """
    # Step 1: Convert document to markdown
    print("Step 1: Converting document to markdown...")
    conversion = processor.convert_only(
        file_path="document.pdf",
        output_dir="output/"
    )
    print(f"✓ Markdown saved to: {conversion['conversion']['markdown_path']}")
    print()
    
    # Step 2: Chunk the markdown
    print("Step 2: Chunking the markdown...")
    chunks = processor.chunk_only(
        markdown_path=conversion['conversion']['markdown_path']
    )
    print(f"✓ Created {len(chunks)} chunks")
    print()
    
    # Step 3: Export to JSON
    print("Step 3: Exporting to JSON...")
    json_path = processor.export_only(
        chunks=chunks,
        output_path="output/chunks.json",
        source_info={
            "source_file": "document.pdf",
            "markdown_file": conversion['conversion']['markdown_path']
        }
    )
    print(f"✓ JSON saved to: {json_path}")
    print()
    
    print("All steps completed successfully!")
    """
    
    print("📝 Benefits of step-by-step processing:")
    print("   - More control over each stage")
    print("   - Can skip steps if already done")
    print("   - Easier to debug issues")
    print("   - Can use different settings per step")
    print()
    print("📝 To run with your document:")
    print("   1. Uncomment the code above")
    print("   2. Replace 'document.pdf' with your file path")
    print("   3. Run: python examples/example_02_step_by_step.py")


if __name__ == "__main__":
    main()

