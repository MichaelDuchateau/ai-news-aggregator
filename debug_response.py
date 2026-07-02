#!/usr/bin/env python3
"""Debug script to inspect web search response structure."""

import os
from anthropic import Anthropic

from src.config import Config, DEFAULT_MODEL

# Set API key
# API key is read from the ANTHROPIC_API_KEY environment variable (see .env)

client = Anthropic()

try:
    model = Config("config/config.yaml").get_model()
except FileNotFoundError:
    model = DEFAULT_MODEL

print("🔍 Making a test search request...\n")

message = client.messages.create(
    model=model,
    max_tokens=4000,
    tools=[{
        "type": "web_search_20250305",
        "name": "web_search"
    }],
    messages=[{
        "role": "user",
        "content": """Search for: AI breakthrough December 2025

For each result, provide:
- Title
- URL
- Brief summary

Format as:
TITLE: [title]
URL: [url]
SUMMARY: [summary]
---"""
    }]
)

print("📋 Response structure:")
print(f"Total blocks: {len(message.content)}\n")

for i, block in enumerate(message.content, 1):
    print(f"\n{'='*60}")
    print(f"Block {i}:")
    print(f"{'='*60}")
    print(f"Type: {block.type}")
    print(f"Block class: {type(block).__name__}")

    # Print all attributes
    print("\nAttributes:")
    for attr in dir(block):
        if not attr.startswith('_'):
            try:
                value = getattr(block, attr)
                if not callable(value):
                    value_str = str(value)[:200]
                    print(f"  {attr}: {value_str}")
            except:
                pass

    # Special handling for different block types
    if hasattr(block, 'text'):
        print(f"\n📄 Text content (first 500 chars):\n{block.text[:500]}")

    if hasattr(block, 'results'):
        print(f"\n🔎 Search results: {len(block.results)} items")
        for j, result in enumerate(block.results[:3], 1):
            print(f"\n  Result {j}:")
            for attr in dir(result):
                if not attr.startswith('_'):
                    try:
                        value = getattr(result, attr)
                        if not callable(value):
                            print(f"    {attr}: {str(value)[:100]}")
                    except:
                        pass

print("\n" + "="*60)
print("Done!")
