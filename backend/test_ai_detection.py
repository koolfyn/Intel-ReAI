#!/usr/bin/env python3
"""
Test AI detection with different types of content
"""
import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.content_detection import ContentDetectionService

async def test_ai_detection():
    """Test AI detection with various content types"""
    print("🔍 Testing AI Detection with Different Content Types\n")

    service = ContentDetectionService()

    # Test cases
    test_cases = [
        {
            "name": "Human-written content",
            "content": "I just had the worst day at work today. My boss was being really unreasonable about the project deadline, and I had to stay late again. The traffic on the way home was terrible too. At least I can relax now with some Netflix. I'm thinking about looking for a new job because this one is just too stressful. The commute is killing me and the pay isn't great either. Maybe I should start applying to some remote positions or companies closer to home. What do you think?",
            "expected": "human"
        },
        {
            "name": "AI-generated content (formal)",
            "content": "In today's rapidly evolving technological landscape, organizations must adapt to emerging trends to maintain competitive advantage. The implementation of innovative solutions requires careful consideration of various factors including scalability, security, and user experience. Furthermore, it is essential to conduct thorough analysis and evaluation to ensure optimal outcomes. Organizations that fail to embrace digital transformation risk falling behind their competitors and losing market share. Therefore, it is imperative to invest in cutting-edge technologies and develop comprehensive strategies that align with business objectives and customer expectations.",
            "expected": "ai"
        },
        {
            "name": "AI-generated content (list format)",
            "content": "Here are the key benefits of implementing this solution:\n\n1. Enhanced efficiency and productivity\n2. Improved user experience\n3. Reduced operational costs\n4. Better scalability\n5. Increased security measures\n6. Streamlined workflows\n7. Better data management\n8. Improved collaboration\n\nIn conclusion, this approach provides significant advantages for organizations seeking to modernize their infrastructure and stay competitive in today's digital economy. The implementation process should be carefully planned and executed to maximize these benefits.",
            "expected": "ai"
        },
        {
            "name": "Mixed content",
            "content": "I think this new AI tool is pretty cool. It can help with writing and stuff. The company says it improves productivity by 40% and reduces errors significantly. I'm not sure if I trust those numbers though. What do you guys think? Has anyone else tried it? I've been using it for a few weeks now and it's been helpful for emails and reports, but I'm still not sure about using it for creative writing. The results are sometimes too generic and lack personality.",
            "expected": "mixed"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print(f"Content: {test_case['content'][:100]}...")

        try:
            result = await service.detect_content(
                content=test_case['content'],
                content_type="post"
            )

            print(f"Result: {'AI Generated' if result['is_ai_generated'] else 'Human Generated'}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Source: {result.get('source', 'unknown')}")
            print(f"Methods: {len(result.get('detection_methods', []))}")

            if result.get('detection_methods'):
                print("Detection indicators:")
                for method in result['detection_methods']:
                    print(f"  - {method.get('indicator', 'Unknown')}")

            print(f"Recommendation: {result['recommendations'][0]['reason'] if result.get('recommendations') else 'None'}")
            print("-" * 50)

        except Exception as e:
            print(f"Error: {e}")
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_ai_detection())
