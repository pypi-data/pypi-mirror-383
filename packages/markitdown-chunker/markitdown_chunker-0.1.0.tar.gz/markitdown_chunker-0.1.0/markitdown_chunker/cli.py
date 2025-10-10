"""
Command-line interface for markitdown-chunker.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from .processor import MarkitDownProcessor
from .converter import MarkdownConverter


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MarkitDown Chunker - Convert documents to markdown, chunk, and export",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a document with default settings
  markitdown-chunker input.pdf output/
  
  # Convert only (no chunking)
  markitdown-chunker input.pdf output/ --convert-only
  
  # Chunk an existing markdown file
  markitdown-chunker document.md output/ --chunk-only
  
  # Custom chunk size and overlap
  markitdown-chunker input.docx output/ --chunk-size 2000 --overlap 400
  
  # Process without markdown-aware splitting
  markitdown-chunker input.pdf output/ --no-markdown-splitter
        """
    )
    
    # Required arguments
    parser.add_argument(
        "input",
        help="Input file path"
    )
    parser.add_argument(
        "output",
        help="Output directory"
    )
    
    # Operation modes
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--convert-only",
        action="store_true",
        help="Only convert to markdown (skip chunking and export)"
    )
    mode_group.add_argument(
        "--chunk-only",
        action="store_true",
        help="Only chunk an existing markdown file (skip conversion)"
    )
    mode_group.add_argument(
        "--no-export",
        action="store_true",
        help="Skip JSON export (only convert and chunk)"
    )
    
    # Chunking options
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Maximum chunk size in characters (default: 1000)"
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=200,
        help="Chunk overlap size in characters (default: 200)"
    )
    parser.add_argument(
        "--no-markdown-splitter",
        action="store_true",
        help="Disable markdown-aware splitting"
    )
    
    # Image options
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Don't save extracted images"
    )
    parser.add_argument(
        "--include-image-summaries",
        action="store_true",
        help="Include image summaries in chunks (requires --image-summarizer)"
    )
    
    # JSON options
    parser.add_argument(
        "--json-indent",
        type=int,
        default=2,
        help="JSON indentation level (default: 2)"
    )
    
    # Utility options
    parser.add_argument(
        "--list-formats",
        action="store_true",
        help="List supported file formats and exit"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Handle utility options
    if args.list_formats:
        print("Supported file formats:")
        for fmt in sorted(MarkdownConverter.SUPPORTED_FORMATS):
            print(f"  {fmt}")
        return 0
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1
    
    # Create processor
    try:
        processor = MarkitDownProcessor(
            chunk_size=args.chunk_size,
            chunk_overlap=args.overlap,
            use_markdown_splitter=not args.no_markdown_splitter,
            json_indent=args.json_indent
        )
    except Exception as e:
        print(f"Error initializing processor: {e}", file=sys.stderr)
        return 1
    
    # Process the file
    try:
        if args.verbose:
            print(f"Processing: {args.input}")
            print(f"Output directory: {args.output}")
        
        if args.convert_only:
            result = processor.convert_only(
                file_path=args.input,
                output_dir=args.output,
                save_images=not args.no_images
            )
            if args.verbose:
                print(f"✓ Converted to: {result['conversion']['markdown_path']}")
        
        elif args.chunk_only:
            # For chunk-only, input must be markdown
            if not args.input.endswith('.md'):
                print("Error: --chunk-only requires a markdown (.md) input file", file=sys.stderr)
                return 1
            
            chunks = processor.chunk_only(markdown_path=args.input)
            
            if args.verbose:
                print(f"✓ Created {len(chunks)} chunks")
            
            # Export if not disabled
            if not args.no_export:
                input_filename = Path(args.input).stem
                json_path = Path(args.output) / f"{input_filename}_chunks.json"
                processor.export_only(
                    chunks=chunks,
                    output_path=str(json_path),
                    source_info={"source_file": args.input}
                )
                if args.verbose:
                    print(f"✓ Exported to: {json_path}")
        
        else:
            # Full pipeline
            result = processor.process(
                file_path=args.input,
                output_dir=args.output,
                save_images=not args.no_images,
                include_image_summaries=args.include_image_summaries,
                skip_export=args.no_export
            )
            
            if args.verbose:
                for step in result['steps_completed']:
                    if step == 'conversion':
                        print(f"✓ Converted to: {result['conversion']['markdown_path']}")
                    elif step == 'chunking':
                        stats = result['chunking']['statistics']
                        print(f"✓ Created {stats['total_chunks']} chunks")
                        print(f"  Average chunk size: {stats['avg_chunk_size']:.0f} characters")
                    elif step == 'export':
                        print(f"✓ Exported to: {result['export']['json_path']}")
        
        if not args.verbose:
            print("✓ Processing complete")
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

