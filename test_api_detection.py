#!/usr/bin/env python3
"""
Test AI detection through the API
"""
import requests
import json

def test_ai_detection_api():
    """Test AI detection through the API"""
    base_url = "http://localhost:8000/api/v1"

    # Test with AI-generated content
    ai_content = """
    In today's rapidly evolving technological landscape, organizations must adapt to emerging trends to maintain competitive advantage.
    The implementation of innovative solutions requires careful consideration of various factors including scalability, security, and user experience.
    Furthermore, it is essential to conduct thorough analysis and evaluation to ensure optimal outcomes.
    Organizations that fail to embrace digital transformation risk falling behind their competitors and losing market share.
    Therefore, it is imperative to invest in cutting-edge technologies and develop comprehensive strategies that align with business objectives and customer expectations.
    """

    print("🤖 Testing AI Detection through API")
    print(f"Content length: {len(ai_content)} characters")
    print(f"Content preview: {ai_content[:100]}...")

    # Test the AI detection endpoint directly
    try:
        response = requests.post(
            f"{base_url}/ai/detect-content",
            json={
                "content": ai_content,
                "content_type": "post"
            },
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ AI Detection Result:")
            print(f"   Is AI Generated: {result.get('is_ai_generated', 'Unknown')}")
            print(f"   Confidence: {result.get('confidence', 0):.2f}")
            print(f"   Source: {result.get('source', 'Unknown')}")
            print(f"   Methods: {len(result.get('detection_methods', []))}")

            if result.get('detection_methods'):
                print("   Detection indicators:")
                for method in result['detection_methods']:
                    print(f"     - {method.get('indicator', 'Unknown')}")

            if result.get('recommendations'):
                print(f"   Recommendation: {result['recommendations'][0].get('reason', 'None')}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ai_detection_api()
