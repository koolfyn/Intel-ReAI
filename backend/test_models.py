#!/usr/bin/env python3
"""
Test script to check available Claude models
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_models():
    print("🔍 Testing Available Claude Models")
    print("=" * 40)

    try:
        from app.config import settings
        import anthropic

        print(f"API Key loaded: {'Yes' if settings.CLAUDE_API_KEY else 'No'}")
        print(f"API Key length: {len(settings.CLAUDE_API_KEY) if settings.CLAUDE_API_KEY else 0}")
        print(f"Current model: {settings.CLAUDE_MODEL}")
        print()

        # Test different model names
        models_to_test = [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-opus-4-1-20250805",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]

        client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)

        for model in models_to_test:
            print(f"Testing model: {model}")
            try:
                response = client.completions.create(
                    model=model,
                    max_tokens_to_sample=10,
                    prompt=f"{anthropic.HUMAN_PROMPT} Say 'test' {anthropic.AI_PROMPT}"
                )
                print(f"  ✅ {model} - Works! Response: {response.completion[:50]}...")
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg or "not_found" in error_msg:
                    print(f"  ❌ {model} - Model not found")
                elif "401" in error_msg or "authentication" in error_msg:
                    print(f"  ❌ {model} - Authentication error")
                else:
                    print(f"  ❌ {model} - Error: {error_msg[:100]}...")
            print()

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_models())
