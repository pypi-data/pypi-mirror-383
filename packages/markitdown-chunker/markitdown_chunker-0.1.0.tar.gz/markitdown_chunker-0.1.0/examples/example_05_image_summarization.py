"""
Example 5: Image Summarization

This example shows how to include AI-powered image descriptions in your chunks.
Useful when documents contain important diagrams, charts, or images.

You'll need to provide your own image summarization function using:
- OpenAI's GPT-4 Vision
- Google's Gemini Vision
- Anthropic's Claude Vision
- Local vision models (BLIP, LLaVA, etc.)
"""

from markitdown_chunker import MarkitDownProcessor


def my_image_summarizer(image_path: str) -> str:
    """
    Custom image summarizer function.
    
    Replace this with your actual implementation using a vision model.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Text description of the image
    """
    # Example placeholder implementation
    # In production, replace with actual vision API call
    
    # Option 1: OpenAI GPT-4 Vision
    """
    import openai
    with open(image_path, "rb") as image_file:
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in detail"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode()}"}}
                    ]
                }
            ]
        )
        return response.choices[0].message.content
    """
    
    # Option 2: Local model (BLIP)
    """
    from transformers import BlipProcessor, BlipForConditionalGeneration
    from PIL import Image
    
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    
    image = Image.open(image_path)
    inputs = processor(image, return_tensors="pt")
    outputs = model.generate(**inputs)
    caption = processor.decode(outputs[0], skip_special_tokens=True)
    return caption
    """
    
    # Placeholder for demonstration
    return f"[Image at {image_path}] - Replace this with actual vision model output"


def main():
    """Demonstrate image summarization in the pipeline."""
    print("=" * 60)
    print("Example 5: Image Summarization")
    print("=" * 60)
    print()
    
    processor = MarkitDownProcessor()
    
    print("✓ Processor created with image summarization support")
    print()
    print("Image summarization will:")
    print("  1. Detect images in the document")
    print("  2. Extract them during conversion")
    print("  3. Generate descriptions using your function")
    print("  4. Include descriptions in chunks")
    print()
    
    # To use with a real file, uncomment and modify:
    """
    result = processor.process(
        file_path="document_with_images.pdf",
        output_dir="output/",
        include_image_summaries=True,
        image_summarizer=my_image_summarizer
    )
    
    print("✓ Processing complete!")
    print(f"  - Markdown: {result['conversion']['markdown_path']}")
    print(f"  - Chunks: {len(result['chunking']['chunks'])}")
    print(f"  - JSON: {result['export']['json_path']}")
    print()
    
    # Find chunks with images
    chunks_with_images = [
        chunk for chunk in result['chunking']['chunks']
        if 'Image Description:' in chunk['text']
    ]
    
    print(f"Found {len(chunks_with_images)} chunks with image descriptions")
    
    for i, chunk in enumerate(chunks_with_images[:3]):  # Show first 3
        print(f"\nChunk {i+1} (excerpt):")
        print(chunk['text'][:200] + "...")
    """
    
    print("📝 To use image summarization:")
    print("   1. Implement the my_image_summarizer() function above")
    print("   2. Add your vision API credentials")
    print("   3. Uncomment the processing code")
    print("   4. Replace 'document_with_images.pdf' with your file")
    print("   5. Run: python examples/example_05_image_summarization.py")
    print()
    print("💡 Recommended vision models:")
    print("   - OpenAI GPT-4 Vision (best quality, paid API)")
    print("   - Google Gemini Vision (good quality, paid API)")
    print("   - Anthropic Claude Vision (good quality, paid API)")
    print("   - BLIP (local, free, decent quality)")
    print("   - LLaVA (local, free, good quality)")


if __name__ == "__main__":
    main()

