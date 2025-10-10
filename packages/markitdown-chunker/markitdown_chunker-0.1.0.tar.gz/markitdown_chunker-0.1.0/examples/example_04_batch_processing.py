"""
Example 4: Batch Processing Multiple Files

This example shows how to process multiple documents at once.
Great for processing entire directories of documents.
"""

from markitdown_chunker import MarkitDownProcessor


def main():
    """Process multiple files in batch."""
    print("=" * 60)
    print("Example 4: Batch Processing")
    print("=" * 60)
    print()
    
    processor = MarkitDownProcessor(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    print("✓ Processor ready for batch processing")
    print()
    
    # To use with real files, uncomment and modify:
    """
    # List of files to process
    files = [
        "documents/report1.pdf",
        "documents/presentation.pptx",
        "documents/spreadsheet.xlsx",
        "documents/article.docx",
        "documents/notes.txt"
    ]
    
    print(f"Processing {len(files)} files...")
    print()
    
    # Process all files
    results = processor.process_batch(
        file_paths=files,
        output_dir="output/batch/"
    )
    
    # Report results
    successful = 0
    failed = 0
    
    for result in results:
        if "error" in result:
            print(f"❌ Failed: {result['input_file']}")
            print(f"   Error: {result['error']}")
            failed += 1
        else:
            print(f"✓ Success: {result['input_file']}")
            print(f"   Chunks: {len(result['chunking']['chunks'])}")
            print(f"   JSON: {result['export']['json_path']}")
            successful += 1
        print()
    
    print("=" * 60)
    print(f"Batch processing complete!")
    print(f"  Successful: {successful}/{len(files)}")
    print(f"  Failed: {failed}/{len(files)}")
    """
    
    print("📝 Batch processing features:")
    print("   - Process multiple files with one call")
    print("   - Automatic error handling per file")
    print("   - Continue on individual failures")
    print("   - Great for automating document workflows")
    print()
    print("📝 To run with your documents:")
    print("   1. Uncomment the code above")
    print("   2. Replace the file paths with your documents")
    print("   3. Run: python examples/example_04_batch_processing.py")
    print()
    print("💡 Pro tip: Use glob patterns to find files:")
    print("   from pathlib import Path")
    print("   files = list(Path('documents/').glob('*.pdf'))")


if __name__ == "__main__":
    main()

