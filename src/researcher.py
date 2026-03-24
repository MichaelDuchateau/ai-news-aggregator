"""Deep dive research module for selected news items."""

from typing import List
from anthropic import Anthropic

from src.models import NewsItem
from src.config import Config
from src.discovery import NewsDiscovery
from src.web_search_agent import WebSearchAgent


class Researcher:
    """Conducts deep dive research on selected news items."""
    
    def __init__(self, config: Config, discovery: NewsDiscovery):
        self.config = config
        self.discovery = discovery
        self.client = Anthropic()
        self.search_agent = WebSearchAgent()  # Dedicated search agent
    
    def deep_dive(self, item: NewsItem) -> NewsItem:
        """Perform deep dive research on a single item."""
        print(f"\n🔬 Deep diving: {item.title[:60]}...")
        
        # 1. Fetch full article content
        print("  📄 Fetching full article...")
        full_content = self.discovery.fetch_full_content(item.url)
        item.content = full_content
        
        # 2. Find related sources
        print("  🔗 Finding related sources...")
        related_sources = self._find_related_sources(item)
        item.research_sources = related_sources
        
        # 3. Fetch content from related sources
        additional_context = []
        for i, source_url in enumerate(related_sources[:3], 1):  # Limit to top 3
            print(f"  📄 Fetching source {i}/3...")
            content = self.discovery.fetch_full_content(source_url)
            if content:
                additional_context.append(content)
        
        # 4. Generate comprehensive narrative
        print("  ✍️  Generating narrative...")
        narrative = self._generate_narrative(item, additional_context)
        item.narrative = narrative
        
        # 5. Refine tags based on deeper understanding
        print("  🏷️  Refining tags...")
        refined_tags = self._refine_tags(item)
        item.tags = refined_tags
        
        # Update status
        item.status = "deep-dive"
        
        print(f"  ✅ Deep dive complete")
        return item
    
    def deep_dive_all(self, items: List[NewsItem]) -> List[NewsItem]:
        """Perform deep dives on all selected items."""
        print(f"\n🔬 Starting deep dives on {len(items)} items...")
        
        for i, item in enumerate(items, 1):
            print(f"\n[{i}/{len(items)}]")
            self.deep_dive(item)
        
        print(f"\n✅ Completed {len(items)} deep dives")
        return items
    
    def _find_related_sources(self, item: NewsItem) -> List[str]:
        """Find related sources for additional context."""
        try:
            # Extract key terms from title
            key_terms = self._extract_key_terms(item.title)

            # Use search agent to find related content
            search_query = f"{key_terms} research papers announcements technical analysis"
            news_items = self.search_agent.search_news(
                query=search_query,
                days_back=30,  # Broader timeframe for related sources
                max_results=5
            )

            # Extract URLs and filter out the original item URL
            urls = [ni.url for ni in news_items if ni.url != item.url]

            return urls[:5]

        except Exception as e:
            print(f"    ⚠️  Error finding related sources: {e}")
            import traceback
            print(f"    Traceback: {traceback.format_exc()}")
            return []
    
    def _extract_key_terms(self, title: str) -> str:
        """Extract key terms from title for searching."""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words = title.lower().split()
        key_words = [w for w in words if w not in stop_words and len(w) > 3]
        return ' '.join(key_words[:5])
    
    def _generate_narrative(self, item: NewsItem, additional_context: List[str]) -> str:
        """Generate comprehensive narrative story."""
        try:
            # Prepare context
            context_text = "\n\n---\n\n".join(additional_context[:2])
            
            min_words, max_words = self.config.get('deep_dive.narrative_length', [500, 800])
            
            prompt = f"""Write a comprehensive, engaging narrative about this AI news story.

Original Article Title: {item.title}
Source: {item.source}
Summary: {item.summary}

Main Article Content:
{item.content[:3000]}

Additional Context from Related Sources:
{context_text[:2000]}

Write a narrative that:
1. Explains what happened and why it matters
2. Provides technical context for informed readers
3. Discusses implications for the AI field
4. Is {min_words}-{max_words} words
5. Is written in clear, engaging prose (not bullet points)
6. Connects this development to broader AI trends

Write the narrative now:"""

            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return message.content[0].text.strip()
        
        except Exception as e:
            print(f"    ⚠️  Error generating narrative: {e}")
            return f"Error generating narrative. Please see original article at {item.url}"
    
    def _refine_tags(self, item: NewsItem) -> List[str]:
        """Refine tags based on deep dive research."""
        try:
            prompt = f"""Based on this comprehensive research, refine the tags for this AI news item.

Title: {item.title}
Current Tags: {', '.join(item.tags)}

Content Summary:
{item.content[:2000]}

Narrative:
{item.narrative[:1000]}

Generate up to 8 refined tags across these categories:
- Topic (max 2): llm, computer-vision, robotics, nlp, reinforcement-learning, etc.
- Company (max 2): openai, anthropic, google, meta, microsoft, etc.
- Type (max 1): research, product, business, policy, tutorial
- Impact (max 1): high, medium, low
- Specialty (max 2): reasoning, multimodal, agents, safety, open-source, etc.

Format: Return ONLY the tags as a comma-separated list with category prefixes.
Example: ai/llm, company/openai, type/research, impact/high, specialty/reasoning

Refined tags:"""

            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = message.content[0].text.strip()
            tags = [tag.strip() for tag in response_text.split(',')]
            tags = [tag for tag in tags if tag]
            
            return tags[:8]
        
        except Exception as e:
            print(f"    ⚠️  Error refining tags: {e}")
            return item.tags  # Return original tags on error
