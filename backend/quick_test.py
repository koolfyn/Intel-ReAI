#!/usr/bin/env python3
"""
Quick API test script with proper error detection
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def quick_test():
    print("🔍 Quick API Test")
    print("-" * 30)

    all_passed = True

    try:
        # Test 1: Import and initialize Claude service
        print("1. Testing Claude service initialization...")
        from app.services.claude_service import ClaudeService
        claude = ClaudeService()
        print(f"   ✅ Model: {claude.model}")

        # Test 2: Make a simple API call
        print("2. Testing Claude API call...")
        response = await claude.generate_response(
            "Say 'Hello from Claude!' and nothing else.",
            max_tokens=20
        )

        # Check if we got the fallback error message
        if "I'm sorry, I'm having trouble processing your request right now." in response:
            print(f"   ❌ API call failed - got fallback error message")
            print(f"   Response: {response}")
            all_passed = False
        else:
            print(f"   ✅ Response: {response}")

        # Test 3: Test RAG components
        print("3. Testing RAG components...")
        from app.services.query_processor import QueryProcessor
        from app.services.retrieval_engine import RetrievalEngine
        from app.services.context_builder import ContextBuilder

        qp = QueryProcessor()
        re = RetrievalEngine()
        cb = ContextBuilder()
        print("   ✅ All RAG components initialized")

        # Test 4: Test query processing
        print("4. Testing query processing...")
        processed = qp.process_query("What is the best programming language?")
        print(f"   ✅ Query processed: {processed['intent']} - {processed['keywords']}")

        if all_passed:
            print("\n🎉 All tests passed! Your API integration is working.")
        else:
            print("\n❌ Some tests failed! Check the errors above.")

        return all_passed

    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)
