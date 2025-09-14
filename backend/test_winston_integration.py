#!/usr/bin/env python3
"""
Test script for Winston AI integration
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.winston_ai_service import WinstonAIService
from app.services.content_detection import ContentDetectionService

async def test_winston_ai():
    """Test Winston AI service directly"""
    print("🤖 Testing Winston AI Service...")

    service = WinstonAIService()

    # Test health check
    health = await service.health_check()
    print(f"Health Check: {health}")

    # Test with sample text
    sample_text = """
    This is a comprehensive analysis of the current market trends in the technology sector.
    The data indicates significant growth opportunities across multiple verticals, particularly
    in artificial intelligence, cloud computing, and cybersecurity. Companies that invest
    strategically in these areas are likely to see substantial returns over the next 3-5 years.

    Key findings include:
    1. AI adoption is accelerating across industries
    2. Cloud migration continues to be a priority
    3. Security concerns are driving increased investment
    4. Remote work trends are reshaping technology needs

    In conclusion, the technology sector presents numerous opportunities for growth and innovation.
    """

    print(f"\n📝 Testing with sample text (length: {len(sample_text)} chars)")
    result = await service.detect_ai_text(sample_text)

    print(f"Result: {result}")
    return result

async def test_content_detection():
    """Test the full content detection service"""
    print("\n🔍 Testing Content Detection Service...")

    service = ContentDetectionService()

    # Test with AI-like content
    ai_content = """
    The implementation of machine learning algorithms has revolutionized the way we approach
    data analysis and pattern recognition. These sophisticated systems leverage advanced
    statistical methods to identify complex relationships within large datasets, enabling
    organizations to make more informed decisions based on empirical evidence rather than
    intuition alone.
    """

    print(f"Testing AI-like content (length: {len(ai_content)} chars)")
    result = await service.detect_content(ai_content, "post")

    print(f"Detection Result:")
    print(f"  - Is AI Generated: {result['is_ai_generated']}")
    print(f"  - Confidence: {result['confidence']:.2f}")
    print(f"  - Source: {result.get('source', 'unknown')}")
    print(f"  - Methods: {len(result.get('detection_methods', []))}")
    print(f"  - Recommendations: {len(result.get('recommendations', []))}")

    return result

async def main():
    """Run all tests"""
    print("🚀 Starting Winston AI Integration Tests\n")

    try:
        # Test Winston AI directly
        winston_result = await test_winston_ai()

        # Test content detection service
        detection_result = await test_content_detection()

        print("\n✅ All tests completed successfully!")

        # Summary
        print(f"\n📊 Summary:")
        print(f"  - Winston AI Health: {winston_result.get('source', 'unknown')}")
        print(f"  - Detection Working: {detection_result.get('is_ai_generated', False)}")
        print(f"  - Confidence: {detection_result.get('confidence', 0):.2f}")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
