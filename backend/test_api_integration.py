#!/usr/bin/env python3
"""
Test script for API integration verification
Tests Claude API, RAG pipeline, and AI companion functionality
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_claude_api():
    """Test basic Claude API functionality"""
    print("🔍 Testing Claude API...")
    try:
        from app.services.claude_service import ClaudeService

        claude = ClaudeService()
        print(f"✅ Claude service initialized with model: {claude.model}")

        # Test simple response
        response = await claude.generate_response(
            "Hello! Please respond with just 'API test successful' and nothing else.",
            max_tokens=50
        )
        print(f"✅ Claude API Response: {response}")
        return True

    except Exception as e:
        print(f"❌ Claude API Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_rag_pipeline():
    """Test RAG pipeline components"""
    print("\n🔍 Testing RAG Pipeline...")
    try:
        from app.services.query_processor import QueryProcessor
        from app.services.retrieval_engine import RetrievalEngine
        from app.services.context_builder import ContextBuilder

        # Test Query Processor
        qp = QueryProcessor()
        processed_query = qp.process_query("What are the best programming languages?")
        print(f"✅ Query Processor: {processed_query['intent']} - {processed_query['keywords']}")

        # Test Retrieval Engine
        re = RetrievalEngine()
        print("✅ Retrieval Engine initialized")

        # Test Context Builder
        cb = ContextBuilder()
        print("✅ Context Builder initialized")

        return True

    except Exception as e:
        print(f"❌ RAG Pipeline Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_ai_companion():
    """Test AI Companion service"""
    print("\n🔍 Testing AI Companion...")
    try:
        from app.services.ai_companion import AICompanionService

        ai_companion = AICompanionService()
        print("✅ AI Companion service initialized")

        # Test with mock database session (we'll create a simple mock)
        class MockDB:
            def query(self, model):
                return self

            def filter(self, *args):
                return self

            def all(self):
                return []

            def limit(self, n):
                return self

        mock_db = MockDB()

        # Test query (this will fail gracefully if no data)
        result = await ai_companion.query_companion(
            query="What is the best way to learn programming?",
            subreddit_id=None,
            context=None,
            db=mock_db
        )

        print(f"✅ AI Companion Response: {result['response'][:100]}...")
        return True

    except Exception as e:
        print(f"❌ AI Companion Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_full_integration():
    """Test full integration with sample data"""
    print("\n🔍 Testing Full Integration...")
    try:
        from app.services.rag_orchestrator import RAGOrchestrator

        # Create sample data
        sample_posts = [
            {
                "id": 1,
                "title": "Best Programming Languages for Beginners",
                "content": "Python is great for beginners because it has simple syntax and many resources.",
                "author": "test_user",
                "score": 10,
                "created_at": "2024-01-01T00:00:00",
                "subreddit_id": 1
            },
            {
                "id": 2,
                "title": "JavaScript vs Python for Web Development",
                "content": "JavaScript is essential for frontend development, while Python is great for backend.",
                "author": "dev_expert",
                "score": 15,
                "created_at": "2024-01-02T00:00:00",
                "subreddit_id": 1
            }
        ]

        sample_comments = [
            {
                "id": 1,
                "content": "I agree, Python is very beginner-friendly!",
                "author": "newbie_dev",
                "post_id": 1,
                "score": 5,
                "created_at": "2024-01-01T01:00:00"
            }
        ]

        # Test RAG Orchestrator
        rag = RAGOrchestrator()

        # Test query processing
        processed_query = rag.query_processor.process_query("What programming language should I learn first?")
        print(f"✅ Query processed: {processed_query['intent']}")

        # Test retrieval
        ranked_content = rag.retrieval_engine.retrieve_relevant_content(
            processed_query, sample_posts, sample_comments
        )
        print(f"✅ Retrieved {len(ranked_content)} relevant items")

        # Test context building
        context_data = rag.context_builder.build_context(
            "What programming language should I learn first?", ranked_content
        )
        print(f"✅ Context built with {context_data['item_count']} items")

        return True

    except Exception as e:
        print(f"❌ Full Integration Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting API Integration Tests")
    print("=" * 50)

    start_time = datetime.now()

    # Run tests
    tests = [
        ("Claude API", test_claude_api),
        ("RAG Pipeline", test_rag_pipeline),
        ("AI Companion", test_ai_companion),
        ("Full Integration", test_full_integration)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nTotal: {passed}/{len(results)} tests passed")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"Duration: {duration:.2f} seconds")

    if passed == len(results):
        print("\n🎉 All tests passed! Your API integration is working correctly.")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please check the errors above.")

    return passed == len(results)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
