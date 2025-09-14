#!/usr/bin/env python3
"""
Test with more obviously AI-generated content
"""
import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.content_detection import ContentDetectionService

async def test_obvious_ai():
    """Test with obviously AI-generated content"""
    print("🤖 Testing with Obviously AI-Generated Content\n")

    service = ContentDetectionService()

    # Test with very obvious AI content
    ai_content = """
    As an AI language model, I must emphasize that the following information is generated for educational purposes only.
    The implementation of machine learning algorithms requires careful consideration of various factors including data quality,
    model architecture, and computational resources. Furthermore, it is essential to conduct thorough testing and validation
    to ensure optimal performance. The following steps outline the recommended approach for developing robust AI systems:

    1. Data Collection and Preprocessing
    2. Model Selection and Architecture Design
    3. Training and Validation
    4. Performance Evaluation
    5. Deployment and Monitoring

    In conclusion, successful AI implementation requires a systematic approach and attention to detail throughout the entire process.
    """

    print(f"Testing with AI content (length: {len(ai_content)} chars)")
    print(f"Content preview: {ai_content[:100]}...")

    try:
        result = await service.detect_content(
            content=ai_content,
            content_type="post"
        )

        print(f"\nResult: {'AI Generated' if result['is_ai_generated'] else 'Human Generated'}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Source: {result.get('source', 'unknown')}")
        print(f"Methods: {len(result.get('detection_methods', []))}")

        if result.get('detection_methods'):
            print("Detection indicators:")
            for method in result['detection_methods']:
                print(f"  - {method.get('indicator', 'Unknown')}")

        print(f"Recommendation: {result['recommendations'][0]['reason'] if result.get('recommendations') else 'None'}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_obvious_ai())
