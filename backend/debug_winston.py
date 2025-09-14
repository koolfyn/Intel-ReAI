#!/usr/bin/env python3
"""
Debug Winston AI response structure
"""
import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.winston_ai_service import WinstonAIService

async def debug_winston():
    """Debug Winston AI response structure"""
    print("🔍 Debugging Winston AI Response Structure\n")

    service = WinstonAIService()

    # Test with sample text
    sample_text = """
    I just had the worst day at work today. My boss was being really unreasonable about the project deadline, and I had to stay late again. The traffic on the way home was terrible too. At least I can relax now with some Netflix. I'm thinking about looking for a new job because this one is just too stressful. The commute is killing me and the pay isn't great either. Maybe I should start applying to some remote positions or companies closer to home. What do you think?
    """

    print(f"Testing with text (length: {len(sample_text)} chars)")

    try:
        result = await service.detect_ai_text(sample_text)
        print(f"Result: {result}")

        # Check the raw response structure
        if 'raw_response' in result:
            print(f"\nRaw response type: {type(result['raw_response'])}")
            print(f"Raw response keys: {list(result['raw_response'].keys()) if isinstance(result['raw_response'], dict) else 'Not a dict'}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_winston())
