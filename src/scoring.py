"""Scoring module for ranking discovered news items."""

from datetime import datetime, timezone
from typing import List
from src.models import NewsItem
from src.config import Config


class NewsScorer:
    """Scores and ranks news items based on configured criteria."""
    
    def __init__(self, config: Config):
        self.config = config
        self.weights = config.get_scoring_weights()
        self.high_value_keywords = [kw.lower() for kw in config.get_high_value_keywords()]
        self.medium_value_keywords = [kw.lower() for kw in config.get_medium_value_keywords()]
    
    def score_all(self, items: List[NewsItem]) -> List[NewsItem]:
        """Score all items and sort by score."""
        print("📊 Scoring news items...")
        
        for item in items:
            item.score = self._calculate_score(item)
        
        # Sort by score descending
        items.sort(key=lambda x: x.score, reverse=True)
        
        print(f"✅ Scored {len(items)} items (range: {items[-1].score:.1f} - {items[0].score:.1f})")
        return items
    
    def _calculate_score(self, item: NewsItem) -> float:
        """Calculate score for a single item."""
        scores = {
            'source_authority': self._score_source_authority(item),
            'recency': self._score_recency(item),
            'uniqueness': self._score_uniqueness(item),
            'keyword_match': self._score_keywords(item)
        }
        
        # Weighted sum
        total_score = sum(
            scores[component] * self.weights.get(component, 0.25)
            for component in scores
        )
        
        # Scale to 0-100
        return min(100, max(0, total_score * 100))
    
    def _score_source_authority(self, item: NewsItem) -> float:
        """Score based on source authority weight."""
        # Source weight is typically 0.8-1.5
        # Normalize to 0-1 range
        return min(1.0, item.source_weight / 1.5)
    
    def _score_recency(self, item: NewsItem) -> float:
        """Score based on how recent the item is."""
        age_days = (datetime.now(timezone.utc) - item.discovered).days
        
        if age_days == 0:
            return 1.0
        elif age_days <= 1:
            return 0.9
        elif age_days <= 3:
            return 0.7
        elif age_days <= 7:
            return 0.5
        elif age_days <= 14:
            return 0.3
        else:
            return 0.1
    
    def _score_uniqueness(self, item: NewsItem) -> float:
        """Score based on content uniqueness."""
        # This is simplified - could be enhanced with:
        # - Title similarity comparison to other items
        # - Content analysis
        # - URL domain diversity
        
        # For now, give base score
        score = 0.5
        
        # Boost for non-aggregator sources
        if any(term in item.source.lower() for term in ['blog', 'paper', 'research', 'official']):
            score += 0.3
        
        # Penalize aggregators
        if any(term in item.source.lower() for term in ['news', 'feed', 'search']):
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _score_keywords(self, item: NewsItem) -> float:
        """Score based on keyword matches in title and summary."""
        text = (item.title + ' ' + (item.summary or '')).lower()
        
        score = 0.0
        
        # High value keywords
        high_matches = sum(1 for kw in self.high_value_keywords if kw in text)
        score += high_matches * 0.15
        
        # Medium value keywords
        medium_matches = sum(1 for kw in self.medium_value_keywords if kw in text)
        score += medium_matches * 0.08
        
        return min(1.0, score)
    
    def get_shortlist(self, items: List[NewsItem], size: int) -> List[NewsItem]:
        """Get top N items for shortlist."""
        min_score = self.config.get('selection.min_score', 40)
        
        # Filter by minimum score and take top N
        qualified = [item for item in items if item.score >= min_score]
        return qualified[:size]
