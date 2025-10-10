"""
Example 3: Custom Chunking Parameters

This example demonstrates how to customize the chunking behavior:
- Custom chunk size and overlap
- Custom markdown headers to split on
- Direct text chunking without file conversion
"""

from markitdown_chunker import DocumentChunker


def main():
    """Demonstrate custom chunking parameters."""
    print("=" * 60)
    print("Example 3: Custom Chunking")
    print("=" * 60)
    print()
    
    # Create chunker with custom parameters
    chunker = DocumentChunker(
        chunk_size=2000,              # Larger chunks
        chunk_overlap=400,             # More overlap
        use_markdown_splitter=True,    # Use markdown-aware splitting
        headers_to_split_on=[
            ("#", "Title"),
            ("##", "Section"),
            ("###", "Subsection"),
            ("####", "Paragraph"),     # Also split on H4
        ]
    )
    
    print("✓ Chunker created with custom settings:")
    print(f"  - Chunk size: 2000 characters")
    print(f"  - Overlap: 400 characters")
    print(f"  - Split on headers: H1, H2, H3, H4")
    print()
    
    # Sample markdown text to chunk
    text = """# Introduction
This is the introduction section with some content. We'll discuss the main topics
and provide an overview of what's covered in this document.

## Background
Here we discuss the background information that's important for understanding
the context. This includes historical perspectives and current state.

### Historical Context
Details about historical context go here. We explore how things evolved over time
and what led to the current situation.

## Main Content
This is where the bulk of the information lives. We dive deep into the technical
details and provide comprehensive explanations.

### Technical Details
Specific technical information and implementation details are provided here.

#### Code Examples
Here we would include actual code snippets and examples to illustrate the concepts.
"""
    
    # Chunk the text
    chunks = chunker.chunk_text(text)
    
    print(f"✓ Created {len(chunks)} chunks from sample text")
    print()
    
    # Display chunk information
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}:")
        print(f"  Text length: {len(chunk['text'])} characters")
        print(f"  Metadata: {chunk['metadata']}")
        print(f"  Preview: {chunk['text'][:80]}...")
        print()
    
    # Get statistics
    stats = chunker.get_statistics(chunks)
    print("Statistics:")
    print(f"  - Total chunks: {stats['total_chunks']}")
    print(f"  - Total characters: {stats['total_characters']}")
    print(f"  - Average chunk size: {stats['avg_chunk_size']:.0f}")
    print(f"  - Min chunk size: {stats['min_chunk_size']}")
    print(f"  - Max chunk size: {stats['max_chunk_size']}")
    print()
    
    print("💡 Tips:")
    print("   - Larger chunk_size = fewer, larger chunks")
    print("   - Larger overlap = more context preserved between chunks")
    print("   - More headers = finer-grained splitting")
    print("   - Adjust based on your use case (embeddings, RAG, etc.)")


if __name__ == "__main__":
    main()

