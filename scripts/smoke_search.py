#!/usr/bin/env python3
"""Manual live-API smoke script for the web search agent.

Not a pytest test — makes real Anthropic API calls. Run directly:
    python scripts/smoke_search.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.web_search_agent import WebSearchAgent
from src.search_debugger import get_debugger


def test_basic_search():
    """Test a basic search query."""
    print("=" * 60)
    print("TEST 1: Basic AI News Search")
    print("=" * 60)

    agent = WebSearchAgent()

    # Test with a simple query
    results = agent.search_news(
        query="AI breakthrough December 2025",
        days_back=7,
        max_results=5
    )

    print(f"\n📊 Results: {len(results)} items found")

    if results:
        print("\n✅ SUCCESS: Search returned results")
        for i, item in enumerate(results, 1):
            print(f"\n{i}. {item.title}")
            print(f"   URL: {item.url}")
            print(f"   Source: {item.source}")
    else:
        print("\n⚠️  WARNING: No results found")

    return len(results) > 0


def test_fetch_content():
    """Test fetching content from a URL."""
    print("\n" + "=" * 60)
    print("TEST 2: Fetch URL Content")
    print("=" * 60)

    agent = WebSearchAgent()

    # Test with a known AI news URL
    test_url = "https://openai.com/news"

    content = agent.fetch_url_content(test_url)

    print(f"\n📊 Content length: {len(content)} characters")

    if content:
        print("\n✅ SUCCESS: Content fetched")
        print(f"\nPreview (first 200 chars):\n{content[:200]}...")
    else:
        print("\n⚠️  WARNING: No content fetched")

    return len(content) > 0


def test_llm_specific_search():
    """Test searching for LLM-specific news."""
    print("\n" + "=" * 60)
    print("TEST 3: LLM-Specific Search")
    print("=" * 60)

    agent = WebSearchAgent()

    results = agent.search_news(
        query="large language model news OR LLM release",
        days_back=14,
        max_results=5
    )

    print(f"\n📊 Results: {len(results)} items found")

    if results:
        print("\n✅ SUCCESS: LLM search returned results")
    else:
        print("\n⚠️  WARNING: No LLM results found")

    return len(results) > 0


def main():
    """Run all tests."""
    print("\n🧪 Web Search Agent Test Suite")
    print("=" * 60)

    results = []

    try:
        # Test 1: Basic search
        results.append(("Basic Search", test_basic_search()))

        # Test 2: Fetch content
        results.append(("Fetch Content", test_fetch_content()))

        # Test 3: LLM search
        results.append(("LLM Search", test_llm_specific_search()))

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    # Print debugger summary
    debugger = get_debugger()
    debugger.print_summary()

    # Exit code
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
