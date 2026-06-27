"""News discovery module for fetching content from various sources."""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List
from anthropic import Anthropic

from src.models import NewsItem, RSSFeed, Website, SearchQuery
from src.config import Config
from src.state_manager import StateManager
from src.web_search_agent import WebSearchAgent


class NewsDiscovery:
    """Discovers news from multiple sources."""
    
    def __init__(self, config: Config, state: StateManager):
        self.config = config
        self.state = state
        self.client = Anthropic()
        self.search_agent = WebSearchAgent(config)
    
    def discover_all(self) -> List[NewsItem]:
        """Discover news from all configured sources."""
        print("🔍 Starting news discovery...")
        
        items = []
        
        # RSS Feeds
        for feed in self.config.get_rss_feeds():
            print(f"  📡 Fetching RSS: {feed.name}")
            items.extend(self._fetch_rss(feed))
        
        # Websites
        for site in self.config.get_websites():
            print(f"  🌐 Scraping: {site.name}")
            items.extend(self._scrape_website(site))
        
        # Search Queries
        for query in self.config.get_search_queries():
            print(f"  🔎 Searching: {query.query[:50]}...")
            items.extend(self._search_web(query))
        
        # Deduplicate
        items = self._deduplicate(items)
        
        print(f"✅ Discovered {len(items)} unique items")
        return items
    
    def _fetch_rss(self, feed: RSSFeed) -> List[NewsItem]:
        """Fetch items from RSS feed."""
        try:
            parsed = feedparser.parse(feed.url)
            items = []
            
            for entry in parsed.entries[:20]:  # Limit to 20 most recent
                url = entry.get('link', '')
                
                # Skip if already processed
                if self.state.is_url_processed(url):
                    continue
                
                # Extract date
                published = entry.get('published_parsed')
                if published:
                    pub_date = datetime(*published[:6])
                else:
                    pub_date = datetime.now()

                # Only include items from last 14 days
                if (datetime.now() - pub_date).days > 14:
                    continue

                item = NewsItem(
                    url=url,
                    title=entry.get('title', 'No title'),
                    source=feed.name,
                    source_weight=feed.weight,
                    discovered=pub_date,
                    summary=entry.get('summary', ''),
                    week=self.state.get_current_week()
                )
                
                items.append(item)
            
            return items
        
        except Exception as e:
            print(f"  ⚠️  Error fetching {feed.name}: {e}")
            return []
    
    def _scrape_website(self, site: Website) -> List[NewsItem]:
        """Scrape news items from a website."""
        try:
            response = requests.get(site.url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find article links
            # This is a simple implementation - may need customization per site
            articles = soup.find_all(['article', 'h2', 'h3'])[:15]
            
            items = []
            for article in articles:
                # Find link
                link = article.find('a')
                if not link or not link.get('href'):
                    continue
                
                url = link['href']
                
                # Make absolute URL if relative
                if url.startswith('/'):
                    from urllib.parse import urljoin
                    url = urljoin(site.url, url)
                
                # Skip if already processed
                if self.state.is_url_processed(url):
                    continue
                
                title = link.get_text(strip=True) or "No title"
                
                item = NewsItem(
                    url=url,
                    title=title,
                    source=site.name,
                    source_weight=site.weight,
                    discovered=datetime.now(),
                    week=self.state.get_current_week()
                )
                
                items.append(item)
            
            return items
        
        except Exception as e:
            print(f"  ⚠️  Error scraping {site.name}: {e}")
            return []
    
    def _search_web(self, query: SearchQuery) -> List[NewsItem]:
        """Search web using dedicated search agent."""
        try:
            # Use the search agent for transparent searching
            items = self.search_agent.search_news(
                query=query.query,
                days_back=query.days_back,
                max_results=10
            )

            # Set the week for all items and filter already processed URLs
            filtered_items = []
            for item in items:
                if not self.state.is_url_processed(item.url):
                    item.week = self.state.get_current_week()
                    filtered_items.append(item)

            if len(items) != len(filtered_items):
                print(f"     ℹ️  Filtered out {len(items) - len(filtered_items)} already-processed URLs")

            return filtered_items

        except Exception as e:
            print(f"  ⚠️  Error searching '{query.query}': {e}")
            return []
    
    def _deduplicate(self, items: List[NewsItem]) -> List[NewsItem]:
        """Remove duplicate items by URL."""
        seen_urls = set()
        unique_items = []
        
        for item in items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        return unique_items
    
    def fetch_full_content(self, url: str) -> str:
        """Fetch full content from a URL for deep dive."""
        try:
            # Use the search agent's fetch capability
            return self.search_agent.fetch_url_content(url)

        except Exception as e:
            print(f"  ⚠️  Error fetching content from {url}: {e}")
            return ""
