"""Web search agent module for transparent search operations."""

from typing import List, Dict, Optional
from datetime import datetime
from anthropic import Anthropic

from src.config import DEFAULT_MODEL
from src.models import NewsItem
from src.search_debugger import get_debugger


class WebSearchAgent:
    """Handles web search operations with transparent logging."""

    def __init__(self, config=None):
        self.client = Anthropic()
        self.model = config.get_model() if config else DEFAULT_MODEL
        self.search_count = 0
        self.debugger = get_debugger()

    def search_news(
        self,
        query: str,
        days_back: int = 7,
        max_results: int = 10,
        source_name: Optional[str] = None
    ) -> List[NewsItem]:
        """
        Search for news articles using web search.

        Args:
            query: Search query string
            days_back: How many days back to search
            max_results: Maximum number of results to return
            source_name: Name to use as source (defaults to query)

        Returns:
            List of NewsItem objects
        """
        self.search_count += 1
        search_id = self.search_count

        print(f"\n  🔎 Search Agent #{search_id}")
        print(f"     Query: {query[:60]}...")
        print(f"     Time range: Last {days_back} days")

        try:
            # Perform the search
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search"
                }],
                messages=[{
                    "role": "user",
                    "content": f"""Search for recent AI news: {query}

Focus on articles from the last {days_back} days.
Return the top {max_results} most relevant results.

For each result, provide:
- Title
- URL
- Brief summary (1-2 sentences)

Format each result as:
TITLE: [article title]
URL: [full URL]
SUMMARY: [brief summary]
---"""
                }]
            )

            # Parse the response
            items = self._parse_search_response(
                message,
                query,
                source_name or f"Web Search: {query[:30]}"
            )

            print(f"     ✅ Found {len(items)} results")

            # Log what was found
            if items:
                print(f"     Top results:")
                for i, item in enumerate(items[:3], 1):
                    print(f"       {i}. {item.title[:50]}...")
            else:
                print(f"     ⚠️  No results found")
                print(f"     Response preview: {str(message.content)[:200]}...")

            # Log to debugger
            full_response = str(message.content)
            self.debugger.log_search(
                query=query,
                results_count=len(items),
                success=True,
                raw_response=full_response,
                parsed_items=[{"title": item.title, "url": item.url} for item in items]
            )

            return items

        except Exception as e:
            print(f"     ❌ Search failed: {e}")
            import traceback
            traceback_str = traceback.format_exc()
            print(f"     Traceback: {traceback_str}")

            # Log error to debugger
            self.debugger.log_search(
                query=query,
                results_count=0,
                success=False,
                error=str(e)
            )

            return []

    def _parse_search_response(
        self,
        message,
        query: str,
        source_name: str
    ) -> List[NewsItem]:
        """Parse Claude's search response into NewsItem objects."""
        items = []

        # Check if web_search tool was actually used
        tool_used = False
        search_results = []

        for block in message.content:
            # Check for server-side tool use
            if hasattr(block, 'type'):
                if block.type == 'server_tool_use':
                    tool_used = True
                    print(f"     ℹ️  Server tool '{block.name}' was invoked")
                elif block.type == 'tool_use':
                    tool_used = True
                    print(f"     ℹ️  Tool '{block.name}' was invoked")

                # Check for web search results block
                if block.type == 'web_search_tool_result':
                    # This contains the actual search results
                    if hasattr(block, 'results'):
                        search_results = block.results
                        print(f"     ℹ️  Found {len(search_results)} raw search results")

        if not tool_used:
            print(f"     ⚠️  Warning: web_search tool was not used in response")

        # Parse search results if we got them directly
        if search_results:
            for result in search_results:
                if hasattr(result, 'url') and hasattr(result, 'title'):
                    item = NewsItem(
                        url=result.url,
                        title=result.title,
                        source=source_name,
                        source_weight=1.0,
                        discovered=datetime.now(),
                        summary=getattr(result, 'snippet', '') or getattr(result, 'description', ''),
                        week=""
                    )
                    items.append(item)

            if items:
                return items

        # Extract text content from all text blocks
        full_text = ""
        for block in message.content:
            if hasattr(block, 'text') and block.type == 'text':
                full_text += block.text + "\n"

        if not full_text.strip():
            print(f"     ⚠️  No text content in response")
            return items

        # Parse structured format (TITLE: / URL: / SUMMARY:)
        entries = full_text.split('---')

        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue

            # Extract title, URL, and summary
            title = None
            url = None
            summary = None

            lines = entry.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('TITLE:'):
                    title = line.replace('TITLE:', '').strip()
                elif line.startswith('URL:'):
                    url = line.replace('URL:', '').strip()
                elif line.startswith('SUMMARY:'):
                    summary = line.replace('SUMMARY:', '').strip()

            # Create NewsItem if we have required fields
            if title and url:
                item = NewsItem(
                    url=url,
                    title=title,
                    source=source_name,
                    source_weight=1.0,
                    discovered=datetime.now(),
                    summary=summary or "",
                    week=""  # Will be set by caller
                )
                items.append(item)

        # Fallback: Try simple URL extraction if structured parsing failed
        if not items:
            print(f"     ℹ️  Trying fallback URL extraction...")
            print(f"     Debug: Full text preview: {full_text[:300]}...")
            items = self._fallback_url_extraction(full_text, source_name)

        return items

    def _fallback_url_extraction(
        self,
        text: str,
        source_name: str
    ) -> List[NewsItem]:
        """Fallback method to extract URLs from unstructured text."""
        items = []
        lines = text.split('\n')

        current_title = None
        current_url = None

        for i, line in enumerate(lines):
            line = line.strip()

            # Check for TITLE: prefix (with or without markdown bold **)
            if 'TITLE:' in line:
                current_title = line.split('TITLE:')[1].strip().strip('*').strip()
                continue

            # Check for URL: prefix (with or without markdown bold **)
            if 'URL:' in line:
                url_part = line.split('URL:')[1].strip().strip('*').strip()
                if url_part.startswith('http'):
                    current_url = url_part
                    # Create item when we have both title and URL
                    if current_title and current_url:
                        item = NewsItem(
                            url=current_url,
                            title=current_title,
                            source=source_name,
                            source_weight=1.0,
                            discovered=datetime.now(),
                            week=""
                        )
                        items.append(item)
                        current_title = None
                        current_url = None
                continue

            # Generic URL extraction (if TITLE:/URL: format didn't work)
            if 'http' in line and not line.startswith(('TITLE:', 'URL:', 'SUMMARY:')):
                # Extract URL
                parts = line.split('http')
                if len(parts) > 1:
                    url = 'http' + parts[1].split()[0].rstrip('.,;:)]}')

                    # Try to extract title (text before URL)
                    title_part = parts[0].strip(' -•*[]()1234567890.')
                    if not title_part and i > 0:
                        # Look at previous line for title
                        title_part = lines[i-1].strip(' -•*[]()1234567890.TITLE:')

                    if title_part:
                        item = NewsItem(
                            url=url,
                            title=title_part,
                            source=source_name,
                            source_weight=1.0,
                            discovered=datetime.now(),
                            week=""
                        )
                        items.append(item)

        return items

    def fetch_url_content(self, url: str) -> str:
        """Fetch full text content from a URL using requests + BeautifulSoup."""
        import requests
        from bs4 import BeautifulSoup

        print(f"\n  📄 Fetching URL: {url}")

        try:
            response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Remove boilerplate elements
            for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
                tag.decompose()

            # Prefer <article> body, fall back to <main>, then <body>
            container = soup.find("article") or soup.find("main") or soup.body
            text = container.get_text(separator="\n", strip=True) if container else ""

            print(f"     ✅ Fetched {len(text)} characters")

            self.debugger.log_fetch(
                url=url,
                content_length=len(text),
                success=bool(text)
            )

            return text

        except Exception as e:
            print(f"     ❌ Fetch failed: {e}")

            self.debugger.log_fetch(
                url=url,
                content_length=0,
                success=False,
                error=str(e)
            )

            return ""
