"""Data models for AI News Aggregator."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl


class NewsItem(BaseModel):
    """Represents a single news article/item."""
    
    url: str
    title: str
    source: str
    source_weight: float
    discovered: datetime
    summary: Optional[str] = None
    content: Optional[str] = None
    score: float = 0.0
    tags: List[str] = []
    status: str = "discovered"  # discovered, scanned, shortlisted, deep-dive
    week: str = ""
    
    # Deep dive specific
    narrative: Optional[str] = None
    research_sources: List[str] = []
    slide_file: Optional[str] = None
    slide_number: Optional[int] = None


class SourceConfig(BaseModel):
    """Configuration for a news source."""
    
    url: str
    name: str
    weight: float = 1.0


class RSSFeed(SourceConfig):
    """RSS feed source."""
    pass


class Website(SourceConfig):
    """Website scraping source."""
    
    selector: Optional[str] = None


class SearchQuery(BaseModel):
    """Search query configuration."""
    
    query: str
    days_back: int = 7
    min_relevance: float = 0.7


class WeeklyState(BaseModel):
    """State tracking for current week."""
    
    week: str
    stage: str  # discovery, scoring, shortlist_review, deep_dive, complete
    items_discovered: int = 0
    items_shortlisted: int = 0
    items_deep_dived: int = 0
    current_processing: Optional[str] = None
    last_updated: datetime
    
    # Track items at each stage
    discovered_urls: List[str] = []
    shortlisted_urls: List[str] = []
    deep_dive_urls: List[str] = []


class ProcessedURL(BaseModel):
    """Tracking for already processed URLs."""
    
    url: str
    first_seen: datetime
    status: str
    week: str
