"""Tag generation module using Claude AI."""

from typing import List
from anthropic import Anthropic

from src.models import NewsItem
from src.config import Config


class NewsTagger:
    """Generates relevant tags for news items using Claude."""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = Anthropic()
        self.max_tags = config.get('obsidian.tag_max', 8)
        self.tag_categories = config.get('obsidian.tag_categories', [])
    
    def tag_item(self, item: NewsItem) -> List[str]:
        """Generate tags for a single news item."""
        
        prompt = f"""Analyze this AI news article and generate relevant tags.

Title: {item.title}
Source: {item.source}
Summary: {item.summary or 'No summary available'}

Generate up to {self.max_tags} tags across these categories:
- Topic (max 2): llm, computer-vision, robotics, nlp, reinforcement-learning, etc.
- Company (max 2): openai, anthropic, google, meta, microsoft, etc.
- Type (max 1): research, product, business, policy, tutorial
- Impact (max 1): high, medium, low
- Specialty (max 2): reasoning, multimodal, agents, safety, open-source, etc.

Format: Return ONLY the tags as a comma-separated list with category prefixes.
Example: ai/llm, company/openai, type/research, impact/high, specialty/reasoning

Tags:"""
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract tags from response
            response_text = message.content[0].text.strip()
            tags = [tag.strip() for tag in response_text.split(',')]
            tags = [tag for tag in tags if tag]  # Remove empty
            
            # Ensure max limit
            return tags[:self.max_tags]
        
        except Exception as e:
            print(f"  ⚠️  Error generating tags: {e}")
            # Fallback to basic tags
            return self._generate_fallback_tags(item)
    
    def _generate_fallback_tags(self, item: NewsItem) -> List[str]:
        """Generate basic fallback tags without API."""
        tags = []
        
        title_lower = item.title.lower()
        source_lower = item.source.lower()
        
        # Topic detection
        if any(term in title_lower for term in ['llm', 'language model', 'gpt', 'claude']):
            tags.append('ai/llm')
        if any(term in title_lower for term in ['vision', 'image', 'visual']):
            tags.append('ai/computer-vision')
        if any(term in title_lower for term in ['robot', 'robotic']):
            tags.append('ai/robotics')
        
        # Company detection
        companies = {
            'openai': 'company/openai',
            'anthropic': 'company/anthropic',
            'google': 'company/google',
            'meta': 'company/meta',
            'microsoft': 'company/microsoft'
        }
        for company, tag in companies.items():
            if company in title_lower or company in source_lower:
                tags.append(tag)
        
        # Type detection
        if any(term in title_lower for term in ['research', 'paper', 'study']):
            tags.append('type/research')
        elif any(term in title_lower for term in ['release', 'launch', 'product']):
            tags.append('type/product')
        elif any(term in title_lower for term in ['policy', 'regulation', 'law']):
            tags.append('type/policy')
        
        # Default impact
        tags.append('impact/medium')
        
        return tags[:self.max_tags]
    
    def tag_all(self, items: List[NewsItem]):
        """Generate tags for all items in place."""
        print("🏷️  Generating tags...")
        
        for i, item in enumerate(items, 1):
            if not item.tags:
                item.tags = self.tag_item(item)
                print(f"  {i}/{len(items)}: {len(item.tags)} tags for '{item.title[:50]}...'")
        
        print(f"✅ Tagged {len(items)} items")
